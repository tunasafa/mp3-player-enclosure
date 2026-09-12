"""Parametric T01 packaging concept. All dimensions in mm, Z front -> rear.
Run from any directory with ../.venv/bin/python touchscreen_01/build.py.
Unknown component envelopes are requirements on future hardware, not fitted products.
"""
from pathlib import Path
import itertools
import json
import math
import hashlib
import cadquery as cq
import trimesh
from cadquery.occ_impl.shapes import sortWiresByBuildOrder

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'parameters.json').read_text())
B, D, F = P['body'], P['display'], P['fasteners']
W,L,T = B['width'], B['length'], B['thickness']
OUT = ROOT/'designs/T01_concept'
TRAY_Z = D['lcd_z']+D['lcd_size'][2]+.2

def block(w,l,h,x=0,y=0,z=0):
    return cq.Workplane('XY').box(w,l,h,centered=(True,True,False)).translate((x,y,z))

def rounded(w,l,h,r=1,x=0,y=0,z=0):
    return block(w,l,h).edges('|Z').fillet(r).translate((x,y,z))

def cyl(r,h,x=0,y=0,z=0):
    return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))

def cavity(z,h):
    return rounded(W-2*B['wall'],L-2*B['wall'],h,B['corner_radius']-B['wall'],z=z)

def bottom_port(w,h,x,z):
    return rounded(w,h,5,min(.7,h/2-.01)).rotate((0,0,0),(1,0,0),90).translate((x,-L/2+3,z))

def placed_xiao():
    e = next(e for e in P['electronics'] if e['id']=='xiao')
    return cq.importers.importStep(str(ROOT.parent/'revision_04/vendor/XIAO-ESP32S3 v2.step')).rotate(
        (0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),-90).translate(
        (e['center'][0]-6.1114,e['center'][1]+1.80475,e['z']+.25))

def ports(a):
    u,j,s = P['ports']['usb'],P['ports']['jack'],P['ports']['microsd']
    a = a.cut(bottom_port(u['width'],u['height'],u['x'],u['z']))
    jack = cyl(j['diameter']/2,5).rotate((0,0,0),(1,0,0),90).translate((j['x'],-L/2+3,j['z']))
    a = a.cut(jack)
    slot = rounded(s['width'],s['height'],6,.35).rotate((0,0,0),(1,1,1),120).translate((W/2-4,s['y'],s['z']))
    return a.cut(slot)

def boss(x,y,z,h):
    return cyl(F['boss_radius'],h,x,y,z).union(block(2.2,2,h,math.copysign(W/2-1.2,x),y,z))

def branding(a):
    art = json.loads((ROOT.parent/'revision_04/assets/mytunas-branding.json').read_text())
    for key,width,cy in [('logo',P['branding']['logo_width'],9),('wordmark',P['branding']['wordmark_width'],-7)]:
        wires=[]
        for contour in art[key]:
            wires.append(cq.Wire.makePolygon([cq.Vector(-x*width,y*width+cy,T-P['branding']['depth']) for x,y in contour[:-1]],close=True))
        wires.sort(key=lambda w:cq.Face.makeFromWires(w).Area(),reverse=True)
        for outer,*holes in sortWiresByBuildOrder(wires):
            face=cq.Face.makeFromWires(outer,holes)
            a=a.cut(cq.Solid.extrudeLinear(face,(0,0,P['branding']['depth']+.1)))
    return a.clean()

def shells():
    front=rounded(W,L,B['front_height'],B['corner_radius']).cut(cavity(B['skin'],B['front_height']+1))
    # Rear-loaded digitizer, exposed touch glass; 0.2 mm perimeter adhesive gap.
    front=front.cut(rounded(D['glass_size'][0]+2*D['pocket_clearance'],D['glass_size'][1]+2*D['pocket_clearance'],5,D['glass_corner_radius'],*D['center'],D['lip_z']))
    front=front.cut(rounded(*D['opening'],6,2.4,*D['center'],-1))
    # Removable battery tray permits rear-loading glass before installing the tray.
    b=P['battery']; x,y=b['center']; w,l,_=b['size']
    shelf=block(39.5,l+1,.6,x,y,TRAY_Z).cut(block(w-2,l-3,1,x,y,TRAY_Z-.1))
    for sx in (-1,1):
        front=front.union(block(3.7,l+1,TRAY_Z-.2-1.4,sx*(W/2-2.85),y,1.4))
    # Front-mounted board lands: 0.2 mm insulating adhesive gap below each PCB.
    for e in P['electronics']:
        if e['id'] not in ('xiao','audio','interface_pcb'): continue
        ex,ey=e['center']; ew,el,_=e['size']
        for sx in (-1,1):
            for sy in (-1,1):
                if e['id']=='interface_pcb':
                    if sy==1: continue  # Keep the glass rear-loading path unobstructed.
                    front=front.union(block(9,2.2,.2,sx*19.5,ey+sy*(el/2-2),e['z']-.4))
                else:
                    front=front.union(block(2.2,2.2,e['z']-.2-.9,ex+sx*(ew/2-2),ey+sy*(el/2-2),.9))
    # Locating fences oppose connector insertion. Adhesive holds lift-out direction.
    for e in P['electronics']:
        if e['id'] in ('xiao','audio'):
            x,y=e['center'];w,l,_=e['size']
            front=front.union(block(w-5,.8,2.4,x,y+l/2+.8,.9))
    front=front.union(block(.8,4,1.4,-18.8,-15,TRAY_Z))
    start=B['front_height']+B['seam_gap']
    rear=rounded(W,L,T-start,B['corner_radius'],z=start).cut(cavity(start-1,T-B['skin']-start+1))
    for sx in (-1,1):
        for y in F['y']:
            x=sx*F['x']
            front=front.union(boss(x,y,TRAY_Z-.05,F['mating_z']-TRAY_Z+.05))
            front=front.cut(cyl(F['pilot_diameter']/2,5,x,y,F['pilot_bottom_z']))
            rear=rear.cut(boss(x,y,start-.1,F['mating_z']-start+.1))
            rear=rear.union(boss(x,y,F['mating_z'],T-.5-F['mating_z']))
            rear=rear.cut(cyl(F['clearance_diameter']/2,T+1,x,y,0))
            rear=rear.cut(cyl(F['head_diameter']/2,3,x,y,F['head_seat_z']))
    # Interrupted seam tongues (0.2 mm side clearance), well outside battery.
    for sx in (-1,1):
        tongue=block(.7,12,1.4,sx*(W/2-2),10,B['front_height']-.5)
        front=front.union(tongue).union(block(1.4,12,.4,sx*(W/2-1.55),10,B['front_height']-.5))
        rear=rear.cut(block(1.1,12.4,1.8,sx*(W/2-2),10,B['front_height']-.7))
    return {'front_bezel':ports(front).clean(),'rear_shell':branding(ports(rear)),'battery_tray':shelf}

def references():
    c={'touch_glass':rounded(*D['glass_size'],D['glass_corner_radius'],*D['center'],D['glass_z']),
       'touch_sensor':rounded(D['glass_size'][0],D['glass_size'][1],D['sensor_thickness'],D['glass_corner_radius'],*D['center'],D['glass_z']+D['glass_size'][2]),
       'touch_lcd_tape':rounded(D['lcd_size'][0],D['lcd_size'][1],D['tape_thickness'],1,*D['center'],D['lcd_z']-D['tape_thickness']).cut(block(D['lcd_size'][0]-2,D['lcd_size'][1]-2,1,*D['center'],D['lcd_z']-.5)),
       'lcd':rounded(*D['lcd_size'],1,*D['center'],D['lcd_z']),
       'battery':block(*P['battery']['size'],*P['battery']['center'],P['battery']['z'])}
    for e in P['electronics']: c[e['id']]=block(*e['size'],*e['center'],e['z'])
    # Onboard audio jack mouth extends beyond the conceptual PCB envelope.
    j=P['ports']['jack']
    mouth=cyl(2.3,1).rotate((0,0,0),(1,0,0),90).translate((j['x'],-39,j['z']))
    c['audio']=c['audio'].union(mouth)
    c['xiao']=placed_xiao()
    return c

def interference(items):
    result=[]
    for (an,a),(bn,b) in itertools.combinations(items.items(),2):
        ba,bb=a.val().BoundingBox(),b.val().BoundingBox()
        if any(getattr(ba,k+'max') <= getattr(bb,k+'min')+1e-6 or getattr(bb,k+'max') <= getattr(ba,k+'min')+1e-6 for k in 'xyz'): continue
        v=a.intersect(b).val().Volume()
        if v>.001: result.append({'a':an,'b':bn,'volume_mm3':round(v,6)})
    return result

def main():
    for folder in ['STL','reference_only']: (OUT/folder).mkdir(parents=True,exist_ok=True)
    parts=shells(); comp=references()
    reserves={r['id']:block(*r['size'],*r['center'],r['z']) for r in P['routing_reserves']}
    report={'status':P['status'],'units':'mm','dimensions_L_W_T':[L,W,T],'collisions':interference(dict(parts,**comp)),
            'reserve_collisions':[c for c in interference(dict(parts,**comp,**reserves)) if (c['a'] in reserves)!=(c['b'] in reserves)],'stls':[]}
    # The panel must be insertable before the removable tray and electronics.
    loading=rounded(D['glass_size'][0],D['glass_size'][1],T,D['glass_corner_radius'],*D['center'],D['glass_z'])
    report['display_rear_loading_sweep_intersection_mm3']=round(loading.intersect(parts['front_bezel']).val().Volume(),6)
    # Containment includes exact vendor XIAO, ports, all allowance boxes and reserves.
    outer=rounded(W,L,T,B['corner_radius'])
    report['outside_case']=[]
    for name,s in dict(comp,**reserves).items():
        v=s.cut(outer).val().Volume()
        if v>.001: report['outside_case'].append({'part':name,'volume_mm3':v})
    assembly=cq.Assembly(name='T01_CONDITIONAL_CONCEPT')
    colors={'front_bezel':(.82,.87,.86),'rear_shell':(.60,.68,.68),'touch_glass':(.04,.06,.07),'lcd':(.25,.29,.31),'battery':(.78,.79,.77),'xiao':(.20,.35,.27),'audio':(.16,.30,.34)}
    for name,s in dict(parts,**comp).items():
        assembly.add(s,name=name if name in parts or name=='xiao' else 'ASSUMED_'+name,color=cq.Color(*colors.get(name,(.28,.48,.38))))
        cq.exporters.export(s,str(OUT/'reference_only'/f'{name}.stl'),tolerance=.04,angularTolerance=.12)
        if name in parts:
            cq.exporters.export(s,str(OUT/f'{name}.step'))
            a=s.rotate((0,0,0),(1,0,0),180) if name=='rear_shell' else s
            bb=a.val().BoundingBox(); a=a.translate((-bb.xmin,-bb.ymin,-bb.zmin))
            path=OUT/'STL'/f'{name}_FIT_CONCEPT.stl'
            cq.exporters.export(a,str(path),tolerance=.03,angularTolerance=.1)
            m=trimesh.load_mesh(path,process=True)
            m.apply_translation([0,0,-m.bounds[0,2]])
            m.export(path)
            report['stls'].append({'file':str(path.relative_to(ROOT)),'cad_valid':s.val().isValid(),'solid_count':len(s.solids().vals()),'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'mesh_bodies':int(m.body_count),'volume_mm3':float(m.volume),'print_min_z':float(m.bounds[0,2])})
    assembly.export(str(OUT/'assembly_ASSUMED_components.step'))
    active=[D['active_diagonal_in']*25.4*n/math.hypot(*D['pixels']) for n in D['pixels']]
    b=P['battery']; baseline=P['baseline']
    report['derived']={'active_area_mm':active,'footprint_reduction_percent':100*(1-W*L/(baseline['width']*baseline['length'])),'volume_reduction_percent':100*(1-W*L*T/(baseline['width']*baseline['length']*baseline['thickness'])),'thickness_reduction_percent':100*(1-T/baseline['thickness']),'battery_rear_gap':T-B['skin']-b['z']-b['size'][2],'lcd_to_battery_shelf_gap':TRAY_Z-D['lcd_z']-D['lcd_size'][2],'screw_tip_z':F['head_seat_z']-F['screw_length'],'screw_engagement':F['mating_z']-(F['head_seat_z']-F['screw_length'])}
    report['nearest_shell_clearance_mm']={name:round(min(s.val().distance(p.val()) for p in parts.values()),4) for name,s in comp.items()}
    report['scope']='Checks nominal geometry, exact unscaled XIAO, component envelopes, empty routing volumes, shell containment and exported mesh validity. Does not establish electrical function, manufacturability of custom PCBs, flex bends, print tolerances, physical fit or runtime.'
    report['passed']=not any(report[k] for k in ['collisions','reserve_collisions','outside_case']) and report['display_rear_loading_sweep_intersection_mm3']<.001 and all(s['cad_valid'] and s['watertight'] and s['winding_consistent'] and s['solid_count']==1 and s['mesh_bodies']==1 and s['volume_mm3']>0 for s in report['stls']) and report['derived']['battery_rear_gap']>=b['rear_reserve_min'] and report['derived']['lcd_to_battery_shelf_gap']>=.19
    (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if not report['passed']: raise SystemExit('Fit validation failed; see validation.json')

if __name__=='__main__': main()
