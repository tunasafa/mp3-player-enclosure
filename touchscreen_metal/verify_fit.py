"""Regression probes for the former silently accepted overlap failure."""
from copy import deepcopy
import json
from build import interference,intersection
from geometry import *
v=json.loads((ROOT/'validation.json').read_text())
assert v['passed']
for key in ['collisions','reserve_collisions','outside_case','port_wall_obstructions']:assert v[key]==[],key
assert v['display_rear_loading_sweep_intersection_mm3']==0
assert v['derived']['dac_max_height_rear_gap']>=.15
assert v['construction']['qualified_for_fabrication'] is False
for mesh in v['stls']:
 assert mesh['solid_count']==mesh['mesh_bodies']==1
 assert mesh['cad_valid'] and mesh['watertight'] and mesh['winding_consistent']
comp,_=components()
# Recreate the actual class of failure: move the battery onto the intact DAC.
b=P['battery'];e=E['audio']
bad_battery=comp['battery'].translate((e['center'][0]-b['center'][0],e['center'][1]-b['center'][1],0))
found=interference({'battery':bad_battery,'actual_dac':comp['audio']})
assert found and sum(c['volume_mm3'] for c in found)>100,'Collision regression was accepted'
# Confirm a blocked wall along each access path is detected, independently of
# the nominal hole having been cut. These blockers are never exported.
blocked=[]
for name,probe in port_tools().items():
 port=port_specs()[name];x,y,z=port['center']
 wall=block(3,3,3,x,y,z-1.5)
 volume=intersection(wall,probe)
 assert volume>1,name
 blocked.append({'port':name,'detected_blocker_mm3':round(volume,4)})
# Vendor point placement should agree with the measured connector recess on
# its requested edge; this catches wrong signs/axis swaps during rotation.
ps=port_specs()
assert abs(ps['jack']['center'][0])<1e-6
assert abs(ps['jack']['center'][1]-(-L/2+.4))<1e-6
assert abs(ps['usb']['center'][0]-(W/2-.4))<1e-6
assert abs(ps['microsd']['center'][0]-(-W/2+.4))<1e-6
result={'passed':True,'parameter_sha256':v['parameter_sha256'],'deliberate_battery_DAC_overlap_detected':found,'deliberate_port_blockers_detected':blocked}
(ROOT/'fit_regression.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: strict fit report, deliberate battery/DAC collision and three blocked-port regression probes')
