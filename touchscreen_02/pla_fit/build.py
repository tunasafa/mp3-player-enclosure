"""Build and audit the M02-P01 PLA fit fixture without changing metal exports."""
import base64
import hashlib
import itertools
import json
import os
import subprocess
import zipfile
from xml.etree.ElementTree import Element, SubElement, tostring
import trimesh
from geometry_pla import *
from validate import intersection, interference

OUT = ROOT / 'parts'


def triangles(shape):
    vertices, faces = shape.val().tessellate(.025, .10)
    return np.array([v.toTuple() for v in vertices])[np.array(faces)]


def mesh(shape):
    t = triangles(shape)
    return trimesh.Trimesh(t.reshape(-1, 3), np.arange(t.size//3).reshape(-1, 3), process=True)


def encode(a):
    return base64.b64encode(np.asarray(a, dtype='<f4').tobytes()).decode()


def validate(parts, printed, reserves, original):
    print('  Pairwise part intersections...', flush=True)
    report = dict(revision='M02-P01', exterior_mm=[64, 128, 8.3], passed=False,
                  physically_tested=False, slicer_verified=False, production_ready=False,
                  scope='Nominal CAD fit, rigid assembly paths, print meshes and bed placement. '
                        'Snap elasticity, extrusion, adhesion and purchased parts require physical trials.',
                  ports=metal.port_specs(), collisions=interference(parts), reserve_collisions=[],
                  exterior_violations=[], port_obstructions=[], mesh_checks={}, unchanged_components={},
                  assembly_checks={}, support_contacts=[], retention_checks={})
    outer = rounded(64, 128, 8.3, 6)
    print('  Print meshes and keepouts...', flush=True)
    for n, s in printed.items():
        volume = s.cut(outer).val().Volume()
        if volume > .001:
            report['exterior_violations'].append([n, volume])
        m = mesh(s)
        report['mesh_checks'][n] = dict(valid=s.val().isValid(), solids=len(s.solids().vals()),
                                       watertight=bool(m.is_watertight),
                                       winding_consistent=bool(m.is_winding_consistent),
                                       bodies=int(m.body_count), volume_mm3=float(m.volume), bounds_mm=bounds(s))
        for rn, r in reserves.items():
            if (v := intersection(s, r)) > .001:
                report['reserve_collisions'].append([n, rn, v])
    for pn, probe in metal.port_tools().items():
        for n in ['front_tray', 'rear_lid']:
            if (v := intersection(probe, parts[n])) > .001:
                report['port_obstructions'].append([pn, n, v])
    for n in parts:
        if n in original and n not in ['display_adhesive', 'display_cushion', 'audio_insulator',
                                       'cell_A_envelope_adhesive', 'cell_B_envelope_adhesive',
                                       'pack_protection_pad', 'xiao_saddle_pad']:
            report['unchanged_components'][n] = parts[n].val().isSame(original[n].val())
    tray = parts['front_tray']
    print('  Screen, battery and board insertion paths...', flush=True)
    # Exact rear-loading sweeps for screen and battery envelopes.
    report['assembly_checks']['screen_loading_mm3'] = intersection(
        block(*metal.D['size'][:2], 10, *metal.D['center'], .55), tray)
    for cell in metal.P['battery_envelopes']:
        report['assembly_checks'][cell['id']+'_loading_mm3'] = intersection(
            rounded(*cell['size'][:2], 10, .8, *cell['center'], cell['z']), tray)
    # Vendor boards lower offset, then slide into their original connector mouths.
    # Gate and battery A are intentionally installed after XIAO insertion.
    for name, shift in [('xiao', (-1.6,0,0)), ('audio',(0,2,0))]:
        bb = bounds(parts[name]); cx=(bb[0][0]+bb[1][0]+shift[0])/2; cy=(bb[0][1]+bb[1][1]+shift[1])/2
        local_tray = tray.intersect(block(bb[1][0]-bb[0][0]+abs(shift[0])+.4,
                                         bb[1][1]-bb[0][1]+abs(shift[1])+.4,20,cx,cy,-.1))
        hits = []
        for z in [9,5,2,1,.5,.2,0]:
            hits.append(intersection(parts[name].translate((shift[0],shift[1],z)), local_tray))
        for t in np.linspace(1, 0, 5):
            hits.append(intersection(parts[name].translate((shift[0]*t,shift[1]*t,0)), local_tray))
        print('    '+name+' path checked', flush=True)
        report['assembly_checks'][name+'_sampled_insertion_mm3'] = max(hits)
    # Boards load vertically into carrier pockets before carrier installation.
    # Remove the SD card first: the inserted card cannot pass the port roof.
    carrier_group = ['carrier','microsd_pcb','microsd_socket','microsd_card',
                     'interface_pcb','display_zif','touch_zif','interface_control']
    sd_group = compound([parts[n] for n in ['microsd_pcb','microsd_socket']])
    hits = []
    for z in np.linspace(9,0,19):
        hits.append(intersection(sd_group.translate((0,0,z)), parts['carrier']))
    report['assembly_checks']['sd_into_carrier_mm3'] = max(hits)
    # Independently check carrier vertical insertion; complete SD sequence is
    # additionally described/checkable in assembly documentation.
    report['assembly_checks']['carrier_vertical_loading_mm3'] = max(
        intersection(parts['carrier'].translate((0,0,z)), tray) for z in np.linspace(8,0,17))
    report['assembly_checks']['loaded_carrier_vertical_loading_mm3'] = max(
        intersection(parts[n].translate((0,0,z)), tray)
        for n in carrier_group if n != 'microsd_card' for z in np.linspace(8,0,17))
    # Lid lowers straight down. Only the two explicit snap teeth may touch the
    # tray during approach; their modeled interference is the intended flex.
    teeth = compound([snap_tooth(-1), snap_tooth(1)])
    rigid_lid = parts['rear_lid'].cut(teeth)
    print('  Lid insertion and release engagement...', flush=True)
    lid_blockers = [s for n,s in parts.items() if n != 'rear_lid']
    report['assembly_checks']['lid_rigid_vertical_loading_mm3'] = max(
        intersection(rigid_lid.translate((0,0,z)), s) for z in [9,6,4,2,1,.5,.25,.1,0] for s in lid_blockers)
    report['snap_approach_interference_mm3'] = max(
        intersection(teeth.translate((0,0,z)), tray) for z in np.linspace(2,0,21))
    # Explicit engagements: upward extraction meets the retaining shoulders,
    # inward tooth displacement clears them. This is geometry, not FEA.
    for sign in [-1,1]:
        tooth = snap_tooth(sign)
        locked = intersection(tooth.translate((0,0,.5)), tray)
        released = intersection(tooth.translate((0,-sign*SNAP_DEFLECTION,.5)), tray)
        report['retention_checks'][str(sign)] = dict(locked_overlap_mm3=locked,
                                                    released_overlap_mm3=released,
                                                    release_travel_mm=SNAP_DEFLECTION)
    # Conservative rectangular volume covering the full tongue's inward flex.
    # Check other components/keepouts, not the surrounding same-part lid skin.
    flex_hits=[]
    for sign in [-1,1]:
        sweep=block(18, .8+SNAP_DEFLECTION, 1.7, -1+SNAP_X,
                    sign*(61.7-SNAP_DEFLECTION/2),6.6)
        for n,s in (parts|reserves).items():
            if n in ['rear_lid','front_tray']:continue
            if (v:=intersection(sweep,s))>.001:flex_hits.append([sign,n,v])
    report['snap_flex_space_collisions']=flex_hits
    for a,b,target in [('carrier','front_tray',0),('display_cushion','carrier',0),
                       ('microsd_pcb','carrier',0),('interface_pcb','carrier',0),
                       ('xiao','front_tray',0),('rear_lid','front_tray',0),
                       ('audio','audio_insulator',0),('touch_glass','display_adhesive',0),
                       ('xiao_gate','gate_tape',0)]:
        report['support_contacts'].append(dict(a=a,b=b,gap_mm=parts[a].val().distance(parts[b].val()),target_mm=target))
    report['counts'] = dict(printed_assembly_parts=4, screws=0, threaded_inserts=0,
                           snap_tongues=2, integrated_dac_landing_pads=3)
    report['thin_features_mm'] = dict(front_skin=.4, rear_skin=.4, carrier_deck=.5,
                                    snap_beam_width=.8, snap_beam_length=18)
    report['derived'] = dict(dac_published_height_roof_gap_mm=.25,
                             battery_expansion_reserve_mm=1.7,
                             printed_dimensions_change_mm=[0,0,0])
    # Deliberate faults verify the checks can reject bad geometry.
    report['fault_probes'] = dict(
        battery_intrusion_detected=intersection(parts['cell_A_envelope'], block(3,3,2,-10,-6,1))>1,
        usb_block_detected=intersection(metal.port_tools()['usb'], block(3,3,3,31.6,-9.99,2.1))>1,
        expansion_intrusion_detected=intersection(reserves['cell_A_expansion'],block(3,3,1,-10,-6,6))>1,
        floating_carrier_detected=parts['carrier'].translate((0,0,.3)).val().distance(tray.val())>.1)
    report['passed'] = (
        not any(report[k] for k in ['collisions','reserve_collisions','exterior_violations','port_obstructions','snap_flex_space_collisions'])
        and all(m['valid'] and m['solids']==1 and m['watertight'] and m['winding_consistent']
                and m['bodies']==1 and m['volume_mm3']>0 for m in report['mesh_checks'].values())
        and all(report['unchanged_components'].values())
        and all(x<.001 for x in report['assembly_checks'].values())
        and all(x['gap_mm']<.005 for x in report['support_contacts'])
        and all(x['locked_overlap_mm3']>.01 and x['released_overlap_mm3']<.001 for x in report['retention_checks'].values())
        and all(report['fault_probes'].values()))
    return report


def write_3mf(shapes):
    ns = 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
    model = Element('model', {'unit':'millimeter', 'xml:lang':'en-US', 'xmlns':ns})
    SubElement(model,'metadata',{'name':'Title'}).text='M02-P01 PLA fit prototype / unsliced / MK3S+'
    resources, build = SubElement(model,'resources'), SubElement(model,'build')
    placements = {'front_tray':(5,5),'rear_lid':(78,5),'carrier':(151,5),
                  'xiao_gate':(155,67),'coupon_receiver':(155,95),'coupon_lid':(155,111)}
    bed = []
    for i,(name,shape) in enumerate(shapes.items(),1):
        m = mesh(print_pose(name,shape));x,y=placements[name]
        obj=SubElement(resources,'object',{'id':str(i),'type':'model','name':name})
        el=SubElement(obj,'mesh');verts=SubElement(el,'vertices');faces=SubElement(el,'triangles')
        for v in m.vertices:
            SubElement(verts,'vertex',dict(zip(['x','y','z'],[f'{q:.6f}' for q in v])))
        for face in m.faces:
            SubElement(faces,'triangle',dict(zip(['v1','v2','v3'],map(str,face))))
        SubElement(build,'item',{'objectid':str(i),'transform':f'1 0 0 0 1 0 0 0 1 {x} {y} 0'})
        size=m.extents;assert x+size[0]<250 and y+size[1]<210
        bed.append(dict(part=name,xy_mm=[x,y],size_mm=size.tolist()))
    with zipfile.ZipFile(ROOT/'M02-P01_MK3S_PLA_UNSLICED.3mf','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('3D/3dmodel.model',tostring(model,encoding='utf-8',xml_declaration=True))
        z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    return bed


def main():
    print('Building M02-P01 PLA fixture...',flush=True)
    parts,visual,meta,printed,reserves,original=make()
    print('Checking solids, component fit, keepouts and assembly paths...',flush=True)
    report=validate(parts,printed,reserves,original)
    report['source_sha256']={str(p.relative_to(ROOT.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [ROOT/'geometry_pla.py',ROOT/'build.py',ROOT/'viewer.js',ROOT/'viewer.html',ROOT.parent/'geometry.py',ROOT.parent/'parameters.json']}
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['mesh_checks','source_sha256','ports']},indent=2),flush=True)
    if not report['passed']:
        raise SystemExit('FAIL: see validation.json; no new print package exported')
    OUT.mkdir(exist_ok=True)
    samples=coupons(printed)
    for name,shape in (printed|samples).items():
        m=mesh(print_pose(name,shape));assert m.is_watertight and m.body_count==1,name
        m.export(OUT/(name+'.stl'))
        cq.exporters.export(shape,str(OUT/(name+'.step')))
    report['bed_layout']=write_3mf(printed|samples)
    report['coupon_mesh_checks']={n:dict(watertight=bool(mesh(s).is_watertight),bodies=int(mesh(s).body_count)) for n,s in samples.items()}
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    assembly=cq.Assembly(name='M02_P01_PLA_FIT_PROTOTYPE')
    specs=[]
    for name,shape in parts.items():
        assembly.add(shape,name=name,color=cq.Color(visual[name][0][0]))
        batches=[]
        if name in ['audio','xiao']:
            path=ROOT.parents[1]/'touchscreen_metal/vendor'/f'{name}_face_meshes.json'
            for batch in json.loads(path.read_text()):
                a=np.frombuffer(base64.b64decode(batch['positions']),dtype='<f4').reshape(-1,3)
                batches.append({'positions':encode(metal.transform_points(name,a)),'color_linear':batch['color']})
        else:
            batches=[dict(positions=encode(triangles(s).reshape(-1,3)),color=color) for color,s in visual[name]]
        specs.append(dict(id=name,**meta[name],bounds_mm=bounds(shape),reserve=False,batches=batches))
    for name,shape in reserves.items():
        specs.append(dict(id=name,label=name.replace('_',' '),kind='reserve',explode=0,
                          source='Unoccupied reserve; never print',bounds_mm=bounds(shape),reserve=True,
                          batches=[dict(positions=encode(triangles(shape).reshape(-1,3)),color='#e6a956')]))
    assembly.export(str(ROOT/'assembly_REFERENCE_ONLY.step'))
    data=dict(parameters=metal.P|{'revision':'M02-P01 PLA fit prototype'},report=report,parts=specs)
    (ROOT/'model.json').write_text(json.dumps(data,separators=(',',':')))
    subprocess.run([str(ROOT.parents[1]/'revision_04/node_modules/.bin/esbuild'),str(ROOT/'viewer.js'),
                    '--bundle','--minify','--format=iife',f'--outfile={ROOT}/viewer.bundle.js'],
                   env=os.environ|{'NODE_PATH':str(ROOT.parents[1]/'revision_04/node_modules')},check=True)
    html=(ROOT/'viewer.html').read_text().replace('__DATA__',json.dumps(data,separators=(',',':'))).replace(
        '__SCRIPT__',(ROOT/'viewer.bundle.js').read_text().replace('</script','<\\/script')).replace(
        '__LICENSE__',(ROOT.parents[1]/'revision_04/vendor/LICENSE-viewer.txt').read_text())
    (ROOT/'preview.html').write_text(html)
    print('PASS: four assembly prints, two coupon prints, 3MF, STEP and offline viewer exported.',flush=True)


if __name__=='__main__':
    main()
