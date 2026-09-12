"""Build the complete M02-02 nominal mechanical assembly; stop on any failure."""
from pathlib import Path
import base64,hashlib,json,os,subprocess
import numpy as np
import trimesh
import cadquery as cq
from geometry import *
from validate import validate
OUT=ROOT/'designs/M02_02'
def packed(a):return base64.b64encode(np.asarray(a,dtype='<f4').tobytes()).decode('ascii')
def triangles(s):
 v,f=s.val().tessellate(.04,.12)
 return np.array([p.toTuple() for p in v])[np.array(f)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 print('Constructing complete M02-02 geometry...',flush=True)
 parts,visual,meta=physical();reserved=reserves()
 print('Checking physical intersections, reservations and assembly access...',flush=True)
 report=validate(parts,reserved,meta)
 report['mesh_checks']=[]
 for n,s in parts.items():
  if meta[n]['kind'] not in ['structure','cover']:continue
  t=triangles(s);m=trimesh.Trimesh(vertices=t.reshape(-1,3),faces=np.arange(t.size//3).reshape(-1,3),process=True)
  report['mesh_checks'].append({'part':n,'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'bodies':int(m.body_count),'positive_volume':bool(m.volume>0)})
 report['passed']=report['passed'] and all(c['watertight'] and c['winding_consistent'] and c['bodies']==1 and c['positive_volume'] for c in report['mesh_checks'])
 report['parameter_sha256']=sha(ROOT/'parameters.json')
 report['source_sha256']={n:sha(ROOT/n) for n in ['geometry.py','validate.py','build.py']}
 deps=['revision_04/vendor/6309.step','revision_04/vendor/XIAO-ESP32S3 v2.step','revision_04/assets/mytunas-branding.json','touchscreen_metal/vendor/audio_face_meshes.json','touchscreen_metal/vendor/xiao_face_meshes.json']
 report['dependency_sha256']={n:sha(ROOT.parent/n) for n in deps}
 report['jack_mouth_mm']=port_specs()['jack']['center'];report['jack_edge']='bottom';report['jack_axis']=[0,-1,0]
 report['vendor_dac_rotation_z_degrees']=-90
 report['battery_pack_selected']=False;report['electronics_routed']=False;report['ip_rating']=None
 report['remaining_release_gates']=['Supplier drawing, maximum tolerances and sample for Startek including active-area offset and folded tails','Approved 1S2P pack including protection, lead routing and charging validation','Completed display/SD interface PCB and firmware bring-up','Manufactured case, retention, cable insertion, load/deflection and drop trials','Silicone cover retention/compression and enclosure ingress testing']
 (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ['cad_parts','dependency_sha256','source_sha256']},indent=2),flush=True)
 if not report['passed']:raise SystemExit('FAILED: no assembly or viewer exported')
 for d in ['STL','reference_only','profiles']:(OUT/d).mkdir(parents=True,exist_ok=True)
 assembly=cq.Assembly(name='MODEL_02_COMPLETE_MECHANICAL_PROTOTYPE');specs=[]
 for n,s in parts.items():
  info=meta[n];batches=[]
  if n in ['audio','xiao']:
   for batch in json.loads((ROOT.parent/'touchscreen_metal/vendor'/f'{n}_face_meshes.json').read_text()):
    a=np.frombuffer(base64.b64decode(batch['positions']),dtype='<f4').reshape(-1,3)
    batches.append({'positions':packed(transform_points(n,a)),'color_linear':batch['color']})
  else:batches=[{'positions':packed(triangles(shape).reshape(-1,3)),'color':c} for c,shape in visual[n]]
  specs.append(dict(id=n,**info,bounds_mm=bounds(s),reserve=False,batches=batches))
  assembly.add(s,name=n,color=cq.Color(visual[n][0][0]))
  cq.exporters.export(s,str(OUT/'reference_only'/f'{n}.stl'),tolerance=.04,angularTolerance=.12)
  if info['kind'] in ['structure','support','cover']:
   cq.exporters.export(s,str(OUT/f'{n}.step'))
   suffix='PA12_FIT_PROTOTYPE' if n=='midframe' or info['kind']=='support' else 'SILICONE_REFERENCE' if info['kind']=='cover' else 'METAL_REFERENCE'
   bb=s.val().BoundingBox();onbed=s.translate((-bb.xmin,-bb.ymin,-bb.zmin))
   cq.exporters.export(onbed,str(OUT/'STL'/f'{n}_{suffix}.stl'),tolerance=.04,angularTolerance=.12)
  if n in ['front_bezel','rear_shell','display_carrier','display_adhesive','display_cushion','front_bond','rear_gasket','rear_liner'] or n.endswith('_adhesive'):
   faces=s.faces('<Z' if n=='rear_shell' else '>Z')
   cq.exporters.export(faces.wires(),str(OUT/'profiles'/f'{n}.dxf'))
 assembly.export(str(OUT/'assembly_NOMINAL.step'))
 # Keep the formerly linked reference filename current for existing bookmarks.
 assembly.export(str(ROOT/'packing_REFERENCE_ONLY.step'))
 reserve_asm=cq.Assembly(name='RESERVED_SPACES_NOT_PHYSICAL_PARTS')
 for n,s in reserved.items():
  reserve_asm.add(s,name=n,color=cq.Color('#c69c47'))
  specs.append(dict(id=n,label=n.replace('_',' '),kind='reserve',explode=0,source='Unoccupied allowance; not physical geometry',bounds_mm=bounds(s),reserve=True,batches=[{'positions':packed(triangles(s).reshape(-1,3)),'color':'#c69c47'}]))
 reserve_asm.export(str(OUT/'reserved_spaces_REFERENCE.step'))
 data={'parameters':P,'report':report,'parts':specs}
 (ROOT/'model.json').write_text(json.dumps(data,separators=(',',':')))
 subprocess.run([str(ROOT.parent/'revision_04/node_modules/.bin/esbuild'),str(ROOT/'viewer.js'),'--bundle','--minify','--format=iife',f'--outfile={ROOT}/viewer.bundle.js'],env=os.environ|{'NODE_PATH':str(ROOT.parent/'revision_04/node_modules')},check=True)
 html=(ROOT/'viewer.html').read_text().replace('__DATA__',json.dumps(data,separators=(',',':'))).replace('__SCRIPT__',(ROOT/'viewer.bundle.js').read_text().replace('</script','<\\/script')).replace('__LICENSE__',(ROOT.parent/'revision_04/vendor/LICENSE-viewer.txt').read_text())
 (ROOT/'preview.html').write_text(html)
 print(f'PASS: exported {len(parts)} physical part groups, {len(reserved)} reservations, complete STEP and offline viewer.',flush=True)
if __name__=='__main__':main()
