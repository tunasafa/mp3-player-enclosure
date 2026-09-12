"""Geometry checks shared by the builder and deliberate-fault regression probes."""
import itertools
from geometry import *

def intersection(a,b):
 aa,bb=bounds(a),bounds(b)
 if any(aa[1][i]<=bb[0][i]+1e-7 or bb[1][i]<=aa[0][i]+1e-7 for i in range(3)):return 0.
 cut=a.intersect(b)
 return max(0,cut.val().Volume()) if cut.vals() else 0.
def interference(items):
 return [dict(a=an,b=bn,volume_mm3=round(v,6)) for (an,a),(bn,b) in itertools.combinations(items.items(),2) if (v:=intersection(a,b))>.001]
def validate(parts,reserved,meta):
 report={'model':P['model'],'revision':P['revision'],'exterior_mm':[W,L,T], 'passed':False,'qualified_for_fabrication':False,
 'physical_collisions':interference(parts),'reserve_collisions':[], 'outside_exterior':[], 'port_wall_obstructions':[],
 'ports':port_specs(),'cad_parts':{},'assembly_checks':{},'screen_stock_confirmed':False,
 'scope':'Exact modeled solids and reserved routing/expansion volumes. Component samples, electronic PCB routing, tolerances and environmental/structural tests are not validated.'}
 for rn,r in reserved.items():
  for pn,p in parts.items():
   v=intersection(r,p)
   if v>.001:report['reserve_collisions'].append(dict(a=rn,b=pn,volume_mm3=round(v,6)))
 report['reserve_collisions']+=interference(reserved)
 outer=rounded(W,L,T,6)
 for n,s in (parts|reserved).items():
  v=s.cut(outer).val().Volume()
  if v>.001:report['outside_exterior'].append(dict(part=n,volume_mm3=round(v,6)))
 for name,probe in port_tools().items():
  for sn in ['front_bezel','rear_shell','midframe']:
   v=intersection(probe,parts[sn])
   if v>.001:report['port_wall_obstructions'].append(dict(port=name,part=sn,volume_mm3=round(v,6)))
 for n,s in parts.items():
  report['cad_parts'][n]={'bounds_mm':bounds(s),'valid':s.val().isValid(),'solids':len(s.solids().vals())}
 # Panel installs from the rear before the retainer/platform. Sweeps must clear
 # the frame and bezel; those are the only rigid parts fitted at that stage.
 sweep=block(*D['size'][:2],T,*D['center'],.55)
 report['assembly_checks']['display_rear_loading_mm3']=sum(intersection(sweep,parts[n]) for n in ['midframe','front_bezel'])
 for cell in P['battery_envelopes']:
  sweep=rounded(*cell['size'][:2],T,.8,*cell['center'],cell['z'])
  report['assembly_checks'][cell['id']+'_rear_loading_mm3']=intersection(sweep,parts['midframe'])
 # Recess, lower into the open frame, then slide the mouth into its port.
 # Batteries, removable stops, covers and harnesses are fitted later.
 # Sampled paths supplement exact final checks; this is not continuous CCD.
 for id,shift in [('xiao',(-1.6,0,0)),('audio',(0,2,0)),('microsd_pcb',(1.6,0,0))]:
  moving=compound([parts['microsd_pcb'],parts['microsd_socket']]) if id=='microsd_pcb' else parts[id]
  hits=[]
  for z in np.linspace(9,0,19):
   pose=moving.translate((shift[0],shift[1],z))
   if (v:=intersection(pose,parts['midframe']))>.001:hits.append({'stage':'lower','offset_z':float(z),'volume_mm3':v})
  for fraction in np.linspace(1,0,17):
   pose=moving.translate((shift[0]*fraction,shift[1]*fraction,0))
   if (v:=intersection(pose,parts['midframe']))>.001:hits.append({'stage':'slide','fraction':float(fraction),'volume_mm3':v})
  report['assembly_checks'][id+'_sampled_insertion_obstruction_mm3']=sum(h['volume_mm3'] for h in hits)
  if hits:report.setdefault('insertion_failures',{})[id]=hits
 # Retainer screws are reached axially with other boards fitted.
 for i,(x,y) in enumerate(C['screw_points']):
  access=cyl(1.2,4,x,y,5.15)
  report['assembly_checks']['carrier_driver_'+str(i+1)+'_mm3']=sum(intersection(access,s) for n,s in parts.items() if n not in ['rear_shell','rear_liner'] and not n.startswith('carrier_screw_'))
 for i,(x,y) in enumerate(P['xiao_clamp']['screw_points']):
  access=cyl(1.2,4,x,y,5.3)
  report['assembly_checks']['xiao_clamp_driver_'+str(i+1)+'_mm3']=sum(intersection(access,s) for n,s in parts.items() if n not in ['rear_shell','rear_liner'] and not n.startswith('xiao_clamp_screw_'))
 # After the rear is removed and two saddle screws withdrawn, the saddle
 # lifts without removing the screen carrier or either battery.
 for dz in [0,.5,1,2,4,8]:
  moving=compound([parts['xiao_saddle'],parts['xiao_saddle_pad']]).translate((0,0,dz))
  blockers=['midframe','audio','xiao','cell_A_envelope','cell_B_envelope','display_carrier']
  report['assembly_checks'][f'xiao_saddle_lift_{dz}_mm3']=sum(intersection(moving,parts[n]) for n in blockers)
 # Rear columns are fastened to the lid. The insulating locating seats remain
 # on the DAC during service, so lifting the lid does not pull on the PCB.
 for dz in [.2,1,3,7]:
  moving=compound([parts[f'dac_retainer_{i}'] for i in range(1,4)]).translate((0,0,dz))
  report['assembly_checks'][f'dac_columns_lift_{dz}_mm3']=sum(intersection(moving,parts[n]) for n in ['midframe','audio','cell_B_envelope'])
 # Contact checks catch an unsupported floating board or missing bond thickness.
 # Zero distance verifies nominal contact only, not adhesive/structural strength.
 seats=[('front_bezel','front_bond'),('front_bond','midframe'),('rear_gasket','rear_shell'),('rear_liner','rear_shell'),('display_adhesive','front_bezel'),('display_adhesive','touch_glass'),('touch_glass','lcd'),('lcd','display_cushion'),('display_cushion','display_carrier'),('display_carrier','midframe'),('audio','audio_insulator'),('xiao','xiao_insulator'),('sd_mount_pad','display_carrier'),('sd_mount_pad','microsd_pcb'),('interface_pad_24','interface_pcb'),('interface_pad_54','interface_pcb'),('pack_protection_pad','pack_protection')]
 seats.append(('midframe','rear_shell'))
 for cell in P['battery_envelopes']:seats.extend([(cell['id'],cell['id']+'_adhesive'),(cell['id']+'_adhesive','front_bezel')])
 for i in range(1,4):seats.extend([(f'dac_seat_{i}','audio'),(f'dac_retainer_{i}',f'dac_seat_{i}'),(f'dac_retainer_{i}','rear_shell')])
 seats.extend([('xiao','xiao_saddle_pad'),('xiao_saddle_pad','xiao_saddle'),('xiao_saddle','midframe')])
 for id,*_ in insert_sites():seats.append((id,'midframe'))
 report['nominal_support_contacts']=[{'a':a,'b':b,'gap_mm':round(parts[a].val().distance(parts[b].val()),6)} for a,b in seats]
 report['derived']={'battery_rear_liner_gap_mm':min(round(B['rear_liner_z']-cell['z']-cell['size'][2],6) for cell in P['battery_envelopes']),'battery_expansion_reserved_mm':1.7,'dac_max_height_rear_gap_mm':round(B['rear_liner_z']-(P['audio']['vendor_origin_translation'][2]+7.1),6),
 'display_side_clearance_mm':(60.8-D['size'][0])/2,'screen_to_retainer_mm':.05,'sd_rear_liner_clearance_mm':round(7.83-(P['microsd']['z']+2.6),6)}
 report['service_design']={'metal_threaded_inserts':len(insert_sites()),'dac_original_holes_used':3,'dac_columns_screw_fastened':True,'xiao_removable_saddle':True,'carrier_welded_ribs':4,'years_of_service_validated':False}
 for id,x,y,top,length,minor,depth in insert_sites():
  # Inserts must be reachable from the open rear, above their installation
  # planes. The intentional interference inside the pilot is heat displaced.
  approach=cyl(1.3,9-top,x,y,top)
  report['assembly_checks'][id+'_rear_install_access_mm3']=intersection(approach,parts['midframe'])
 report['passed']=not any(report[k] for k in ['physical_collisions','reserve_collisions','outside_exterior','port_wall_obstructions']) and all(x<=.001 for x in report['assembly_checks'].values()) and all(p['valid'] for p in report['cad_parts'].values()) and all(report['cad_parts'][n]['solids']==1 for n,m in meta.items() if m['kind']=='structure') and report['derived']['dac_max_height_rear_gap_mm']>=.15 and all(c['gap_mm']<=.005 for c in report['nominal_support_contacts'])
 return report

if __name__=='__main__':
 parts,_,meta=physical();report=validate(parts,reserves(),meta)
 (ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k!='cad_parts'},indent=2))
