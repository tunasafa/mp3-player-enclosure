"""Authoritative M02-02 geometry. All visible physical geometry is fit checked.
Millimetres; XY is face plane; Z runs from front toward rear.
"""
from pathlib import Path
from functools import lru_cache
import json, math
import numpy as np
import cadquery as cq
from cadquery.occ_impl.shapes import sortWiresByBuildOrder
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text());B=P['body'];D=P['display'];C=P['carrier']
W,L,T=P['exterior'];F=P['case_fasteners']

def block(w,l,h,x=0,y=0,z=0):return cq.Workplane('XY').box(w,l,h,centered=(True,True,False)).translate((x,y,z))
def rounded(w,l,h,r=.5,x=0,y=0,z=0):return block(w,l,h).edges('|Z').fillet(r).translate((x,y,z))
def cyl(r,h,x=0,y=0,z=0):return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))
def compound(items):return cq.Workplane('XY').newObject([cq.Compound.makeCompound([s.val() for s in items])])
def bounds(s):
 b=s.val().BoundingBox();return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]
def ring(w,l,h,iw,il,r=.5,x=0,y=0,z=0):return rounded(w,l,h,r,x,y,z).cut(rounded(iw,il,h+1,min(r,.4),x,y,z-.5))
def dac_points(a):return np.column_stack((a[:,1],-a[:,0],a[:,2]))+np.array(P['audio']['vendor_origin_translation'])
def xiao_points(a):
 x,y=P['xiao']['center'];z=P['xiao']['z']
 return np.column_stack((a[:,0]-1.80475+x,-a[:,2]-6.1114+y,a[:,1]+.25+z))
def transform_points(id,a):return dac_points(a) if id=='audio' else xiao_points(a)
@lru_cache(maxsize=2)
def vendor(id):
 path=ROOT.parent/'revision_04/vendor'/('6309.step' if id=='audio' else 'XIAO-ESP32S3 v2.step')
 s=cq.importers.importStep(str(path))
 if id=='audio':return s.rotate((0,0,0),(0,0,1),-90).translate(tuple(P['audio']['vendor_origin_translation']))
 x,y=P['xiao']['center'];return s.rotate((0,0,0),(1,0,0),90).translate((x-1.80475,y-6.1114,P['xiao']['z']+.25))
@lru_cache(maxsize=1)
def usb_wire():
 mouth=xiao_points(np.array([[13.8086398,2.705,-6.1114]]))[0,0]
 fs=[f for f in vendor('xiao').val().Faces() if f.geomType()=='PLANE' and abs(f.Center().x-mouth)<1e-4 and len(f.Wires())==2]
 assert len(fs)==1
 return fs[0].outerWire()
def side_profile(w,h,depth,x,y,z,r=.4):
 return rounded(w,h,depth,r).rotate((0,0,0),(1,1,1),120).translate((x-depth/2,y,z))
def usb_tool():
 f=cq.Face.makeFromWires(usb_wire().offset2D(.15)[0])
 return cq.Workplane('XY').newObject([cq.Solid.extrudeLinear(f,(8,0,0))]).translate((-3.6,0,0))
def port_specs():
 u=usb_wire().BoundingBox();j=dac_points(np.array([[33.5370095,16.7591527,3.87248296]]))[0]
 return {'usb':{'edge':'right','center':[u.xmax,(u.ymin+u.ymax)/2,(u.zmin+u.zmax)/2],'width':9.24,'height':3.51,'radial_allowance':.15},
 'jack':{'edge':'bottom','center':j.tolist(),'diameter':5},
 'microsd':{'edge':'left','center':[-31.6,29,P['microsd']['z']+1.55],'width':11.5,'height':1.5}}
def port_tools():
 u,j,s=(port_specs()[n] for n in ['usb','jack','microsd'])
 return {'usb':usb_tool(),'jack':cyl(2.5,8).rotate((0,0,0),(1,0,0),90).translate((j['center'][0],-60,j['center'][2])),
 'microsd':side_profile(11.5,1.5,8,-32,29,s['center'][2])}
def head(x,y):return cq.Workplane('XY').newObject([cq.Solid.makeCone(.8,1.6,.8)]).translate((x,y,7.5))
def carrier_holes(shape,r=.8,z=0,h=10):
 for x,y in C['screw_points']:shape=shape.cut(cyl(r,h,x,y,z))
 return shape

def cover_pockets():
 u,j,s=(port_specs()[n] for n in ['usb','jack','microsd'])
 return {'usb':side_profile(12.6,6,.5,31.8,u['center'][1],u['center'][2],1.4),
 'microsd':side_profile(13.2,2.6,.5,-31.8,s['center'][1],s['center'][2],.6),
 'jack':cyl(3.25,.5).rotate((0,0,0),(1,0,0),90).translate((j['center'][0],-63.55,j['center'][2]))}

def brand(rear):
 art=json.loads((ROOT.parent/'revision_04/assets/mytunas-branding.json').read_text())
 for key,width,cy in [('logo',18,5),('wordmark',22,-11)]:
  wires=[cq.Wire.makePolygon([cq.Vector(-x*width,y*width+cy,8.27) for x,y in c[:-1]],close=True) for c in art[key]]
  wires.sort(key=lambda w:cq.Face.makeFromWires(w).Area(),reverse=True)
  for outer,*holes in sortWiresByBuildOrder(wires):rear=rear.cut(cq.Solid.extrudeLinear(cq.Face.makeFromWires(outer,holes),(0,0,.1)))
 return rear.clean()

def physical():
 parts={};visual={};meta={}
 def add(id,shape,color,label,kind='component',explode=0,source='Designed nominal geometry'):
  parts[id]=shape;visual[id]=[(color,shape)];meta[id]={'label':label,'kind':kind,'explode':explode,'source':source}
 # Continuous enclosure structure, rebuilt for this layout rather than using
 # old screen/battery screw positions. Rails stop short of protected cells.
 frame=rounded(W,L,7.2,6,z=.55).cut(rounded(60.8,124.8,9,4.4,z=.4))
 for x,y in F['points']:
  frame=frame.union(cyl(1.9,7.2,x,y,.55))
  # Positive compression stops support the rear at Z7.90. The perimeter
  # gasket occupies 0.15 mm; screw tightening cannot collapse that gap freely.
  frame=frame.union(cyl(1.8,.15,x,y,7.75))
  if abs(x)>27:frame=frame.union(block(3,2.6,7.2,math.copysign(30.2,x),y,.55))
 # Lower screw island ties to the bottom perimeter, outside both pouches.
 frame=frame.union(block(3.8,3.6,7.2,0,-62,.55))
 # Battery guide rails. Adhesive pads restrain Z; no clip compresses a pouch.
 for yy in [-19.55,7.25]:frame=frame.union(block(40.5,.6,1.2,-10.75,yy,.55))
 frame=frame.union(block(.4,27.4,1.2,-29.5,-6.15,.55))
 for xx in [-29.1,-2.4]:frame=frame.union(block(.6,38.6,1.2,xx,-40.5,.55))
 for yy in [-59.6,-21.4]:frame=frame.union(block(29.4,.6,1.2,-16.6,yy,.55))
 # DAC rails and stop react jack insertion. No change to the vendor PCB.
 for xx in [1.5,28.1]:frame=frame.union(block(.6,33.7,1.7,xx,-46.3,.55))
 # XIAO rear and end stops, bonded dielectric pad below the whole PCB.
 for yy in [-19.55,-.55]:frame=frame.union(block(22.7,.6,1.7,19.75,yy,.55))
 # Four pillars flank the LCD outline, keeping screw heads off the glass.
 for x,y in C['screw_points']:
  frame=frame.union(cyl(1.7,3.8,x,y,.55))
  edge=math.copysign(30.6,x)
  frame=frame.union(block(abs(edge-x)+1,1.3,2,(edge+x)/2,y,.55))
 # Connector reliefs stop before the external wall; exact exterior cuts below.
 ps=port_specs();u,j,sd=(ps[n] for n in ['usb','jack','microsd'])
 frame=frame.cut(block(4,12,4.8,29,u['center'][1],u['center'][2]-2.4))
 frame=frame.cut(block(8,4,6.2,j['center'][0],-61,j['center'][2]-3.1))
 frame=frame.cut(block(4,15,3,-29,29,sd['center'][2]-1.5))
 # Wide LCD tail gets a local side-wall rebate; radius/route remains provisional.
 frame=frame.cut(block(.9,28,3.5,30.45,39,2.3))
 for cutter in port_tools().values():frame=frame.cut(cutter)
 for cutter in cover_pockets().values():frame=frame.cut(cutter)
 # Lead exits through rails, never through the outer skin.
 for tool in [block(12,2,2,3,-21,.8),block(.8,3,2,8.5,-18.5,.8)]:frame=frame.cut(tool)
 for x,y in F['points']:frame=frame.cut(cyl(.65,6,x,y,2.7)).cut(head(x,y))
 for x,y in C['screw_points']:frame=frame.cut(cyl(.55,3.2,x,y,1.4))
 add('midframe',frame.clean(),'#3d555a','PA12 frame / guides and pillars','structure',12)
 # Bezel opening follows the published viewing area; offset remains a sample check.
 front=rounded(W,L,.4,6).cut(rounded(*D['window'],1,.35,*D['window_center'],-.2))
 rear=rounded(W,L,.4,6,z=7.9)
 for x,y in F['points']:rear=rear.cut(cyl(.9,2,x,y,7)).cut(head(x,y))
 add('front_bezel',front,'#acb9bd','Front steel / 0.40 mm','structure',-32)
 add('rear_shell',brand(rear),'#a5b4ba','Rear steel / 0.40 mm','structure',42)
 for id,z in [('front_bond',.4),('rear_gasket',7.75)]:
  g=ring(W,L,.15,61.2,125.2,6,z=z)
  for x,y in F['points']:g=g.cut(cyl(1.85,1,x,y,z-.2))
  add(id,g,'#393f41',id.replace('_',' ')+' / 0.15 mm','seal',-28 if id=='front_bond' else 36)
 # Separate display layers stay within the manufacturer's full 3.75 mm envelope.
 gx,gy,gh=D['glass_size'];lx,ly,lh=D['lcd_size'];dx,dy=D['center']
 add('touch_glass',block(gx,gy,gh,dx,dy,.55),'#142d34','Startek capacitive glass / nominal 1.25 mm','component',-22,'Startek listing; sample drawing required')
 add('lcd',block(lx,ly,lh,dx,dy,1.8),'#a7b2b5','Startek LCD + backlight / nominal 2.50 mm','component',-18,'Startek outline; layer split pending supplier drawing')
 adhesive=ring(gx-.3,gy-.3,.15,*D['window'],.35,dx,dy,.4)
 add('display_adhesive',adhesive,'#56523d','Continuous display bond / 0.15 mm','seal',-25)
 # Steel retainer and separate upper-board platform; pressure spread over perimeter.
 carrier=carrier_holes(rounded(*C['size'],1,*C['center'],C['z']))
 for x,y in F['points']:carrier=carrier.cut(cyl(2.2,1,x,y,4))
 # Access window for provisional folded display/touch tails.
 carrier=carrier.cut(block(7,29,1,26,39,4.2))
 add('display_carrier',carrier,'#8e9f9b','Display retainer / 0.20 mm stainless','structure',8)
 support=ring(58,41,.05,54,37,.4,0,35,4.3).cut(block(8,29,1,26,39,4.2))
 add('display_cushion',support,'#455d58','LCD perimeter cushion / 0.05 mm','seal',6)
 # Retainer ribs on rear surface bridge the thin plate without loading the LCD.
 for yy in [15,56]:
  id='carrier_rib_'+str(yy).replace('.','_')
  add(id,block(44,1.2,1.15,-2,yy,4.6),'#647d76','Bonded retainer stiffening rib','support',10)
  add(id+'_bond',block(44,1.2,.05,-2,yy,4.55),'#baa060','Retainer rib bond / 0.05 mm','seal',9)
 # Boards retain their original manufacturer mesh/geometry and dimensions.
 for id,label in [('audio','Adafruit 6309 / original bottom jack'),('xiao','Seeed XIAO ESP32-S3 / USB right')]:
  add(id,vendor(id),'#397368',label,'component',16,'Unscaled manufacturer STEP')
 a=P['audio']['vendor_origin_translation'];pad=block(25.4,31.75,.15,a[0]+12.7,a[1]-31.75/2,.4)
 add('audio_insulator',pad,'#bb9c52','DAC insulating adhesive / 0.15 mm','seal',3)
 x,y=P['xiao']['center'];add('xiao_insulator',block(20.9,17.7,.35,x,y,.4),'#bb9c52','XIAO insulating adhesive / 0.35 mm','seal',3)
 # Fit these stops after sliding connector mouths into the wall openings.
 add('xiao_insertion_stop',block(.5,15.4,1.7,8.65,-8.75,.55),'#586f68','Removable XIAO insertion stop','support',15)
 add('xiao_stop_adhesive',block(.5,15.4,.15,8.65,-8.75,.4),'#b89c52','XIAO stop bonding pad','seal',2)
 add('dac_insertion_stop',block(25,.6,1.7,14.8,-29.5,.55),'#586f68','Removable DAC insertion stop','support',15)
 add('dac_stop_adhesive',block(25,.6,.15,14.8,-29.5,.4),'#b89c52','DAC stop bonding pad','seal',2)
 # Nonconductive spacers seat on the three actual DAC mounting-hole annuli.
 holes=dac_points(np.array([[2.54,22.86,0],[29.21,2.54,0],[29.21,22.86,0]]))
 for i,(x,y,z) in enumerate(holes):
  spacer=cyl(1.85,7.8-(z+1.57),x,y,z+1.57).union(cyl(.85,1.57,x,y,z))
  add('dac_retainer_'+str(i+1),spacer,'#687f70','DAC locating spacer '+str(i+1),'support',30)
  add('dac_retainer_bond_'+str(i+1),cyl(1.85,.1,x,y,7.8),'#baa060','DAC spacer rear bond / 0.10 mm','seal',32)
 liner=rounded(60.4,124.4,.07,4.2,z=7.83)
 for x,y in F['points']:liner=liner.cut(cyl(2,1,x,y,7.5))
 for x,y,z in holes:liner=liner.cut(cyl(1.95,1,x,y,7.5))
 add('rear_liner',liner,'#c4a45d','Rear dielectric liner / 0.07 mm','seal',38)
 for cell in P['battery_envelopes']:
  id=cell['id'];x,y=cell['center'];w,l,h=cell['size'];z=cell['z']
  # Pouch and gold end tape are disjoint subdivisions of the same envelope.
  pouch=rounded(w,l,h,.8,x,y,z);tape=block(w-1,2.5,.08,x,y+l/2-1.5,z+h-.08)
  add(id,pouch,'#bdc8c5','Battery '+('A' if '_A_' in id else 'B')+' / finished pack allocation','component',18,'DTP502535 max pack dimensions; combined pack unselected')
  visual[id]=[('#bdc8c5',pouch.cut(tape)),('#c89d38',tape)]
  add(id+'_adhesive',rounded(w-2,l-2,.3,.6,x,y,.4),'#504f42','Battery insulating retention pad / 0.30 mm','seal',2)
 # SD board: conservative socket with real slot and finite inserted card.
 e=P['microsd'];x,y=e['center'];z=e['z'];pcb=rounded(*e['pcb_size'],.5,x,y,z)
 cage=block(15.7,14.2,1.8,-23,29,z+.8).cut(block(16,13,1.5,-23.5,29,z+.85))
 card=block(15,11,1,-24.1,29,z+1.05)
 add('microsd_pcb',pcb,'#367464','microSD adapter PCB / nominal 22 × 18','component',20)
 add('microsd_socket',cage,'#b6c2c8','microSD socket / conservative envelope','component',21)
 add('microsd_card',card,'#263033','microSD card','component',22)
 # Dielectric board pads on carrier, plus lateral stop strips resisting insertion.
 add('sd_mount_pad',block(20,16,.3,-18.9,29,4.55),'#b89d59','SD insulating adhesive / 0.30 mm','seal',12)
 # Stops are bonded to the retainer, mechanically separate support parts.
 for yy in [19.5,38.5]:
  id='sd_stop_'+str(yy).replace('.','_')
  add(id,block(20,.5,.95,-18,yy,4.6),'#586f68','SD edge stop','support',14)
  add(id+'_bond',block(20,.5,.05,-18,yy,4.55),'#baa060','SD stop bond / 0.05 mm','seal',12)
 add('sd_insertion_stop',block(.6,17,.95,-7.3,29,4.6),'#586f68','SD insertion load stop','support',14)
 add('sd_insertion_stop_bond',block(.6,17,.05,-7.3,29,4.55),'#baa060','SD insertion stop bond / 0.05 mm','seal',12)
 e=P['interface'];x,y=e['center'];z=e['z'];add('interface_pcb',rounded(*e['size'],.4,x,y,z),'#367464','45P display / touch interface PCB allocation','component',20)
 # Board support lands avoid the retainer's flex slot.
 for yy in [24,54]:add('interface_pad_'+str(yy),block(7,1.4,.3,18,yy,4.55),'#b89d59','Interface insulating mounting land','seal',12)
 add('display_zif',block(5,26.5,1.1,24.8,39,5.65).cut(block(2,23,.3,26.5,39,5.9)),'#333b3f','LCD ZIF / 45P 0.5 mm allocation','component',22)
 add('touch_zif',block(3.5,5,1.1,17,27,5.65),'#333b3f','Touch ZIF / supplier pinout pending','component',22)
 add('interface_control',block(6,12,1.1,17,41,5.65),'#263b39','I/O + backlight control allocation','component',22)
 # Protection location and strain relief: pending battery supplier circuit.
 e=P['pack_protection'];add('pack_protection',block(*e['size'],*e['center'],e['z']),'#596b49','1S2P pack protection allocation','component',17)
 add('pack_protection_pad',block(23,2.5,.3,-10,10,.4),'#b89d59','Pack protection adhesive pad','seal',2)
 # All fasteners are nominal drawing references. No threads are falsely modeled.
 for i,(x,y) in enumerate(F['points']):
  screw=cyl(.625,4.2,x,y,3.3).union(head(x,y)).cut(block(2,.4,.25,x,y,8.1))
  add('case_screw_'+str(i+1),screw,'#b0b8bc','M1.6 × 5 case screw '+str(i+1),'fastener',48)
 for i,(x,y) in enumerate(C['screw_points']):
  screw=cyl(.5,3,x,y,1.55).union(cyl(1.1,.6,x,y,4.55)).cut(block(1.5,.3,.2,x,y,5))
  add('carrier_screw_'+str(i+1),screw,'#b0b8bc','M1.4 × 3 retainer screw '+str(i+1),'fastener',25)
 # Removable flush cover prototypes in their installed/compressed geometry.
 # They close the sockets externally, without entering their contact cavities.
 # The small frame recess is a sealing land, not a qualified retention system.
 u,j,s=(port_specs()[n] for n in ['usb','jack','microsd'])
 cap=side_profile(12.6,6,.4,31.8,u['center'][1],u['center'][2],1.4)
 rim=side_profile(12.6,6,.05,31.575,u['center'][1],u['center'][2],1.4)
 uf=cq.Face.makeFromWires(usb_wire())
 clear=cq.Workplane('XY').newObject([cq.Solid.extrudeLinear(uf,(-.2,0,0))])
 cap=cap.union(rim.cut(clear))
 add('usb_cover',cap,'#283e41','Flush USB-C silicone cover / prototype','cover',25)
 cap=side_profile(13.2,2.6,.4,-31.8,29,s['center'][2],.6)
 rim=side_profile(13.2,2.6,.05,-31.575,29,s['center'][2],.6).cut(port_tools()['microsd'])
 add('sd_cover',cap.union(rim),'#283e41','Flush SD silicone cover / prototype','cover',25)
 cap=cyl(3.25,.4).rotate((0,0,0),(1,0,0),90).translate((j['center'][0],-63.6,j['center'][2]))
 rim=cyl(3.25,.05).cut(cyl(2.5,.2,z=-.05)).rotate((0,0,0),(1,0,0),90).translate((j['center'][0],-63.55,j['center'][2]))
 add('jack_cover',cap.union(rim),'#283e41','Flush jack silicone cover / prototype','cover',25)
 return parts,visual,meta

def reserves():
 r={}
 for cell in P['battery_envelopes']:
  w,l,h=cell['size'];r[cell['id'].replace('envelope','expansion')]=block(w,l,1.7,*cell['center'],cell['z']+h)
 r['cell_link_route']=block(12,2,2,3,-21,.8)
 r['cell_link_turn']=block(.8,3,2,8.5,-18.5,.8)
 # Ribbon/controller route is an explicit keepout, not invented connected flex.
 r['display_tail_fold']=block(.6,23,3.2,30.55,39,2.4)
 r['display_tail_rear']=block(3,23,.25,28.65,39,5.95)
 r['audio_harness']=block(2,8,2,14,-24,3)
 r['main_harness']=block(5,8,1.5,17,6,2)
 return r
