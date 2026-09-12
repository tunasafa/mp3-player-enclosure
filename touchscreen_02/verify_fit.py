"""Deliberate failure probes for overlap, port blockage and floating board seats."""
import hashlib,json
from geometry import *
from validate import intersection,interference
v=json.loads((ROOT/'validation.json').read_text());assert v['passed']
assert v['qualified_for_fabrication'] is False
for n,h in v['source_sha256'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h
assert hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest()==v['parameter_sha256']
parts,_,_=physical();r=reserves()
# A battery placed on the real board must fail; no manufactured outer box is substituted.
bad=parts['cell_A_envelope'].translate((25.3,-40.7,0))
hit=interference({'bad_battery':bad,'actual_DAC':parts['audio']});assert hit and sum(x['volume_mm3'] for x in hit)>100
blockers=[]
for name,probe in port_tools().items():
 x,y,z=port_specs()[name]['center'];wall=block(3,3,3,x,y,z-1.5)
 volume=intersection(wall,probe);assert volume>1
 blockers.append({'port':name,'detected_mm3':round(volume,4)})
# Actual Seeed rim must fit the shaped aperture; the check uses the original wire.
rim=cq.Face.makeFromWires(usb_wire());shell_probe=cq.Workplane('XY').newObject([cq.Solid.extrudeLinear(rim,(.4,0,0))])
assert shell_probe.cut(usb_tool()).val().Volume()<1e-6
assert len(usb_wire().Edges())==8
# Filling reserved expansion space and lifting a board off its mount are distinct failures.
expanded_hit=intersection(parts['cell_A_envelope'].translate((0,0,.5)),r['cell_A_expansion'])
assert expanded_hit>100
floating_gap=parts['microsd_pcb'].translate((0,0,.2)).val().distance(parts['sd_mount_pad'].val())
assert floating_gap>.19
assert all(x<=.001 for x in v['assembly_checks'].values())
assert all(x['gap_mm']<=.005 for x in v['nominal_support_contacts'])
result={'passed':True,'parameter_sha256':v['parameter_sha256'],'deliberate_battery_DAC_collision':hit,'deliberate_port_blockers':blockers,'expansion_violation_detected_mm3':expanded_hit,'floating_board_gap_detected_mm':floating_gap,'source_scope':'Fault injection into physical CAD and independent vendor-rim check'}
(ROOT/'fit_regression.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: real-DAC collision, three port blockers, expansion intrusion, floating board and actual USB rim checks')
