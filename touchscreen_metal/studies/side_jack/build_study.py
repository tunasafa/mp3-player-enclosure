"""Conditional packing study, not an enclosure release or battery-pack design.
Uses unscaled vendor boards; all other parts are explicitly named envelopes.
"""
from pathlib import Path
import sys, json, base64, subprocess, os, hashlib
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from geometry import block, rounded, bounds, vendor, transform_points, components
from build import interference, intersection, triangles, packed
import cadquery as cq

def main():
 dac_offset=np.array([31.6-33.5370095,-50.7,.55])
 dac=cq.importers.importStep(str(ROOT.parent/'revision_04/vendor/6309.step')).translate(tuple(dac_offset))
 reference_parts,reference_visual=components()
 parts={
  'startek_envelope':block(60.26,42.92,3.75,0,35,.55),
  'audio':dac,
  'xiao':vendor('xiao').translate((0,-22,0)),
  'cell_A_envelope':rounded(37,25.5,5.2,.8,-10.5,-6,.7),
  'cell_B_envelope':rounded(25.5,37,5.2,.8,-15.75,-40.5,.7),
  'microsd_nominal':reference_parts['microsd'].translate((0,17,3.75)),
  'interface_envelope':block(12,24,1.9,21,38,4.5),
 }
 reserves={
  'cell_A_expansion':block(37,25.5,1.7,-10.5,-6,5.9),
  'cell_B_expansion':block(25.5,37,1.7,-15.75,-40.5,5.9),
  'pack_protection_and_leads':block(26,4,3,-10,10,.7),
  'screen_tail_and_zif':block(56,5,2.7,0,17,4.5),
  'cell_link_route':block(12,2,2,3,-21,.8),
  'cell_link_turn':block(.8,3,2,8.5,-18.5,.8),
 }
 # Full published DAC dimensions, not the lower maximum of the STEP model.
 dac_max=block(33.7,25.4,7.1,31.6-33.7/2,-38,.55)
 physical=interference(parts)
 reserve_hits=[dict(reserve=rn,part=pn,volume_mm3=round(v,6)) for rn,r in reserves.items() for pn,p in parts.items() if (v:=intersection(r,p))>.001]
 reserve_hits+=interference(reserves)
 dac_hits=[dict(part=pn,volume_mm3=round(v,6)) for pn,p in (parts|reserves).items() if pn!='audio' and (v:=intersection(dac_max,p))>.001]
 outer=rounded(64,128,8.3,6)
 outside=[dict(part=pn,volume_mm3=round(v,6)) for pn,p in (parts|reserves).items() if (v:=p.cut(outer).val().Volume())>.001]
 report={'scope':'Packing envelopes only. No enclosure mounts, actual Startek flex, completed battery pack or seals are validated.',
  'exterior_mm':[64,128,8.3], 'screen_stock_confirmed':False,'qualified_for_fabrication':False,
  'physical_collisions':physical,'reserve_collisions':reserve_hits,'published_dac_envelope_collisions':dac_hits,'outside_exterior':outside,
  'nominal_packing_passed':not(physical or reserve_hits or dac_hits or outside),
  'screen_side_clearance_to_existing_1_6mm_wall':.27,
  'screen_to_underlying_electronics_gap_mm':.2,
  'battery_rear_liner_gap_mm':1.93,'battery_expansion_reserved_mm':1.7,
  'dac_rear_liner_gap_mm':.18,
  'battery_basis':'Each 37 x 25.5 x 5.2 mm envelope uses DTP502535 published maximum pack dimensions. Two 400 mAh cells suggest an 800 mAh target, but a matched supplier-built 1S2P assembly is unselected. Do not parallel two retail protected packs.',
  'jack_mouth_mm':(np.array([33.5370095,16.7591527,3.87248296])+dac_offset).tolist(),
  'bounds_mm':{n:bounds(s) for n,s in (parts|reserves).items()},
  'single_rectangular_alternative':'A single 37 x 25.5 mm envelope fits the same upper battery bay; no larger stocked single pack has been selected. One continuous L cell requires custom tooling/quotation.',
  'remaining_work':['Exact Startek sample availability, drawing, pinout and initialization','Flex fold and latch insertion sweep','New screw and board-retention layout','Cell supplier design including protection, leads, insulation and charger review','USB/SD/headphone sealing and physical testing'],
  'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 if not report['nominal_packing_passed']:raise RuntimeError(json.dumps(report,indent=2))
 meshes=[];a=cq.Assembly(name='CONDITIONAL_PACKING_STUDY_NOT_FOR_FABRICATION')
 colors={'startek_envelope':'#253941','audio':'#406a91','xiao':'#3b8879','cell_A_envelope':'#bdc5bd','cell_B_envelope':'#bdc5bd','microsd_nominal':'#548a78','interface_envelope':'#b38b56'}
 for name,s in (parts|reserves).items():
  batches=[]
  if name in ['audio','xiao']:
   for batch in json.loads((ROOT/'vendor'/f'{name}_face_meshes.json').read_text()):
    vertices=np.frombuffer(base64.b64decode(batch['positions']),dtype='<f4').reshape(-1,3)
    vertices=vertices+dac_offset if name=='audio' else transform_points('xiao',vertices)+np.array([0,-22,0])
    batches.append({'positions':packed(vertices),'color_linear':batch['color']})
  elif name=='microsd_nominal':
   batches=[{'positions':packed(triangles(shape.translate((0,17,3.75))).reshape(-1,3)),'color':color} for color,shape in reference_visual['microsd']]
  else:batches=[{'positions':packed(triangles(s).reshape(-1,3)),'color':colors.get(name,'#c69c47')}]
  meshes.append({'id':name,'bounds_mm':bounds(s),'reserve':name in reserves,'batches':batches})
  a.add(s,name=name,color=cq.Color(colors.get(name,'#c69c47')))
 a.export(str(HERE/'packing_REFERENCE_ONLY.step'))
 data={'report':report,'parts':meshes}
 (HERE/'model.json').write_text(json.dumps(data,separators=(',',':')))
 subprocess.run([str(ROOT.parent/'revision_04/node_modules/.bin/esbuild'),str(HERE/'viewer.js'),'--bundle','--minify','--format=iife',f'--outfile={HERE}/viewer.bundle.js'],env=os.environ|{'NODE_PATH':str(ROOT.parent/'revision_04/node_modules')},check=True)
 html=(HERE/'viewer.html').read_text().replace('__DATA__',json.dumps(data,separators=(',',':'))).replace('__SCRIPT__',(HERE/'viewer.bundle.js').read_text().replace('</script','<\\/script')).replace('__LICENSE__',(ROOT.parent/'revision_04/vendor/LICENSE-viewer.txt').read_text())
 (HERE/'preview.html').write_text(html)
 print('PASS: conditional packing volumes. Exported study STEP and offline viewer; no finished enclosure claim.')
if __name__=='__main__':main()
