"""Strict nominal-fit build. CAD and viewer share geometry.py and its transforms.
No collision exemptions; failed builds cannot generate a new viewer.
"""
import base64, hashlib, itertools, json, math, sys
import numpy as np
import cadquery as cq
import trimesh
from geometry import *
OUT=ROOT/'designs/T03_metal'

def packed(a):return base64.b64encode(np.asarray(a,dtype='<f4').tobytes()).decode('ascii')
def triangles(s):
 vertices,faces=s.val().tessellate(.04,.12)
 return np.array([v.toTuple() for v in vertices])[np.array(faces)]
def intersection(a,b):
 aa,bb=bounds(a),bounds(b)
 if any(aa[1][i]<=bb[0][i]+1e-7 or bb[1][i]<=aa[0][i]+1e-7 for i in range(3)):return 0.
 return max(0,a.intersect(b).val().Volume())
def interference(items):
 result=[]
 for (an,a),(bn,b) in itertools.combinations(items.items(),2):
  v=intersection(a,b)
  if v>.001:result.append(dict(a=an,b=bn,volume_mm3=round(v,6)))
 return result

def main():
 print('Building common CAD geometry...',flush=True)
 parts=shells();comp,visual=components();allparts=parts|comp
 reserves={r['id']:block(*r['size'],*r['center'],r['z']) for r in P['routing_reserves']}
 report={'revision':P['revision'],'status':P['status'],'passed':False,'units':'mm','dimensions_W_L_T':[W,L,T],
 'collisions':interference(allparts),'reserve_collisions':[], 'outside_case':[], 'stls':[], 'ports':port_specs()}
 for rn,r in reserves.items():
  for pn,p in allparts.items():
   v=intersection(r,p)
   if v>.001:report['reserve_collisions'].append(dict(a=rn,b=pn,volume_mm3=round(v,6)))
 outer=rounded(W,L,T,6)
 for name,s in (comp|reserves).items():
  v=s.cut(outer).val().Volume()
  if v>.001:report['outside_case'].append(dict(part=name,volume_mm3=round(v,6)))
 loading=rounded(*D['glass_size'][:2],T,D['glass_corner_radius'],*D['center'],D['glass_z'])
 report['display_rear_loading_sweep_intersection_mm3']=round(sum(intersection(loading,parts[n]) for n in ['front_bezel','midframe']),6)
 # Empty physical access volumes through the case skin, from outside to the
 # connector mouth. Full mouth-size probes catch misplaced or blocked apertures.
 report['port_wall_obstructions']=[]
 for name,probe in port_tools().items():
  for sn in ['front_bezel','rear_shell','midframe']:
   v=intersection(probe,parts[sn])
   if v>.001:report['port_wall_obstructions'].append(dict(port=name,shell=sn,volume_mm3=round(v,6)))
 # Manufacturer's maximum DAC height remains reserved above actual STEP.
 e=E['audio'];dacmax=block(25.4,33.7,7.1,*e['center'],e['z'])
 maxroof=e['z']+7.1;rearinside=T-B['skin']-.07
 b=P['battery'];baseline=P['baseline']
 report['derived']={'active_area_mm':[D['active_diagonal_in']*25.4*n/math.hypot(*D['pixels']) for n in D['pixels']],
 'battery_rear_gap':round(rearinside-b['z']-b['size'][2],6),'dac_max_height_rear_gap':round(rearinside-maxroof,6),
 'thickness_reduction_percent':100*(1-T/baseline['thickness']),
 'footprint_reduction_percent':100*(1-W*L/(baseline['width']*baseline['length'])),
 'volume_reduction_percent':100*(1-W*L*T/(baseline['width']*baseline['length']*baseline['thickness']))}
 report['thickness_study']={'basis':'0.4 mm metal faces, 0.15 mm under-DAC allocation, full 7.1 mm published height, 0.07 mm rear liner and 0.15 mm free rear clearance. Aggressive nominal stack; tolerance and structural qualification outstanding.',
 'minimum_mm':round(E['audio']['z']+7.1+P['minimum_rear_component_clearance']+B['skin']+.07,3),
 'candidates':[{'thickness_mm':t,'dac_rear_clearance_mm':round(t-B['skin']-.07-maxroof,3),'meets_rear_clearance':t-B['skin']-.07-maxroof>=P['minimum_rear_component_clearance']-1e-6} for t in [7.8,8.0,8.1,8.2,8.3,8.5,8.8]]}
 report['construction']={'front_metal_mm':.4,'rear_metal_mm':.4,'rear_liner_mm':.07,'frame_material':'PA12 candidate','nominal_dac_rear_clearance_mm':report['derived']['dac_max_height_rear_gap'],'plate_flatness_and_total_tolerance_budget_mm':.15,'qualified_for_fabrication':False,'remaining_tests':['Measure finished DAC incl solder','Dielectric and wire exit clearance','Metal plate flatness and deflection','Fastener clamp load and plug insertion','Real display tails / SD socket fit']}
 report['cad_parts']={name:{'bounds_mm':bounds(s),'valid':s.val().isValid(),'solids':len(s.solids().vals())} for name,s in allparts.items()}
 report['scope']='All inter-part CAD intersections, empty routing allowances, outer containment, panel insertion, shell continuity and port cutters. Vendor internal construction is retained. Flex geometry, connector selection, solder/lead details, tolerances and real assembly remain unverified. Screw root geometry omits threads.'
 for name,s in parts.items():
  tri=triangles(s);m=trimesh.Trimesh(vertices=tri.reshape(-1,3),faces=np.arange(tri.size//3).reshape(-1,3),process=True)
  report['stls'].append(dict(part=name,cad_valid=s.val().isValid(),solid_count=len(s.solids().vals()),watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),mesh_bodies=int(m.body_count),volume_mm3=float(m.volume)))
 report['passed']=not any(report[k] for k in ['collisions','reserve_collisions','outside_case','port_wall_obstructions']) and report['display_rear_loading_sweep_intersection_mm3']<=.001 and all(s['cad_valid'] and s['solid_count']==1 and s['mesh_bodies']==1 and s['watertight'] and s['winding_consistent'] and s['volume_mm3']>0 for s in report['stls']) and all(p['valid'] for p in report['cad_parts'].values()) and report['derived']['battery_rear_gap']>=b['rear_reserve_min'] and report['derived']['dac_max_height_rear_gap']>=P['minimum_rear_component_clearance']-1e-6
 report['parameter_sha256']=hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest()
 report['source_sha256']={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['geometry.py','build.py']}
 (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='cad_parts'},indent=2),flush=True)
 if not report['passed']:raise SystemExit('Fit validation failed. No new deliverables exported.')
 print('Validation passed. Exporting authoritative geometry...',flush=True)
 for d in ['STL','reference_only']:(OUT/d).mkdir(parents=True,exist_ok=True)
 specs=[];assembly=cq.Assembly(name='T03_METAL_AGGRESSIVE_PROTOTYPE')
 shellcolors={'front_bezel':'#aeb9bd','rear_shell':'#a3afb5','midframe':'#344a4d','display_carrier':'#768b80'}
 labels={'touch_glass':'Cover glass / 43 × 36','touch_sensor':'Capacitive sensor / 0.7 mm','touch_lcd_tape':'LCD perimeter tape','lcd':'LCD / metal backlight pan','display_adhesive':'Glass perimeter adhesive','battery':'503040 LiPo / nominal 600 mAh','battery_foam':'Battery insulating foam','display_flex':'Display ribbon / side route','touch_flex':'Touch ribbon / side route','case_screws':'Six flush M1.6 × 5 screws','front_bezel':'0.4 mm steel front face','rear_shell':'0.4 mm steel rear face','midframe':'PA12 internal frame','dac_retention':'DAC mounting-hole spacers','front_bond':'Front perimeter bond / 0.15 mm','rear_gasket':'Rear perimeter gasket / 0.15 mm','carrier_screws':'Two M1 carrier screws','rear_liner':'Rear dielectric liner / 0.07 mm','audio_insulator':'DAC dielectric pad / 0.15 mm','xiao_insulator':'XIAO dielectric pad / 0.35 mm','microsd_insulator':'SD dielectric pad / 0.35 mm','display_carrier':'0.4 mm metal display retainer'}
 ex={'front_bezel':-1,'touch_glass':-.9,'display_adhesive':-.95,'touch_sensor':-.8,'touch_lcd_tape':-.72,'lcd':-.65,'display_carrier':.1,'rear_shell':1.4,'rear_liner':1.3,'rear_gasket':1.2,'dac_retention':1.0,'midframe':.5,'case_screws':1.6,'display_flex':-.3,'touch_flex':-.3}
 for name,s in allparts.items():
  color=shellcolors.get(name,'#397466');group='shell' if name in parts else 'components'
  source='Unscaled manufacturer STEP' if name in ['audio','xiao'] else 'Nominal CAD; sample dimensions required' if group=='components' else 'T03 enclosure CAD'
  spec=dict(id=name,label=labels.get(name,E.get(name,{}).get('label',name)),group=group,color=color,explode=ex.get(name,.4),source=source,bounds_mm=bounds(s))
  assembly.add(s,name=name,color=cq.Color(color))
  path=OUT/'reference_only'/f'{name}.stl';cq.exporters.export(s,str(path),tolerance=.04,angularTolerance=.12)
  spec['stl_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  if name in ['audio','xiao']:
   # Cache untransformed manufacturer face colors. Rigid transformation is shared.
   sys.path.insert(0,str(ROOT.parent/'revision_04'))
   from make_components import vendor_meshes
   cache=ROOT/'vendor'/f'{name}_face_meshes.json'
   if cache.exists():batches=json.loads(cache.read_text())
   else:
    batches=vendor_meshes('dac' if name=='audio' else 'xiao',lambda a:a);cache.write_text(json.dumps(batches))
   spec['batches']=[]
   for batch in batches:
    a=np.frombuffer(base64.b64decode(batch['positions']),dtype='<f4').reshape(-1,3)
    spec['batches'].append({'color_linear':batch['color'],'positions':packed(transform_points(name,a))})
  elif name in visual:
   spec['batches']=[{'color':c,'positions':packed(triangles(shape).reshape(-1,3))} for c,shape in visual[name]]
  else:spec['batches']=[{'color':color,'positions':packed(triangles(s).reshape(-1,3))}]
  specs.append(spec)
  if name in parts:
   cq.exporters.export(s,str(OUT/f'{name}.step'))
   if name in ['front_bezel','rear_shell','display_carrier']:
    # Rear profile uses underside pilot holes, before countersinking;
    # etched artwork is a separate marking operation, never a through-cut.
    cq.exporters.export(s.faces('<Z' if name=='rear_shell' else '>Z').wires(),str(OUT/f'{name}_profile.dxf'))
    if name=='rear_shell':
     mark=[wire for face in s.val().Faces() if face.geomType()=='PLANE' and abs(face.Center().z-(T-P['branding']['depth']))<1e-5 for wire in face.Wires()]
     cq.exporters.export(cq.Workplane('XY').newObject(mark),str(OUT/'rear_marking_ONLY.dxf'))
   a=s.rotate((0,0,0),(1,0,0),180) if name=='rear_shell' else s
   bb=a.val().BoundingBox();a=a.translate((-bb.xmin,-bb.ymin,-bb.zmin))
   suffix='FIT_PROTOTYPE' if name=='midframe' else 'METAL_REFERENCE'
   cq.exporters.export(a,str(OUT/'STL'/f'{name}_{suffix}.stl'),tolerance=.04,angularTolerance=.12)
 assembly.export(str(OUT/'assembly_NOMINAL_components.step'))
 (ROOT/'model_data.json').write_text(json.dumps({'parameters':P,'parts':specs,'validation':report},separators=(',',':')))
 print('Exported T03 assembly and shared viewer meshes.',flush=True)
if __name__=='__main__':main()
