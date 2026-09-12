"""Common millimetre geometry for CAD, collisions, and the offline viewer.
Z points from the touch face to the rear. No rendered substitute vendor models.
"""
from pathlib import Path
import json, math
import cadquery as cq
import numpy as np
from cadquery.occ_impl.shapes import sortWiresByBuildOrder
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text()); B=P['body']; D=P['display']; F=P['fasteners']
W,L,T=B['width'],B['length'],B['thickness']
E={e['id']:e for e in P['electronics']}

def block(w,l,h,x=0,y=0,z=0):
 return cq.Workplane('XY').box(w,l,h,centered=(True,True,False)).translate((x,y,z))
def rounded(w,l,h,r=1,x=0,y=0,z=0):
 return block(w,l,h).edges('|Z').fillet(r).translate((x,y,z))
def cyl(r,h,x=0,y=0,z=0):
 return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))
def compound(shapes):
 return cq.Workplane('XY').newObject([cq.Compound.makeCompound([s.val() if isinstance(s,cq.Workplane) else s for s in shapes])])
def bounds(s):
 b=s.val().BoundingBox();return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]

def vendor_pose(id):
 e=E[id];x,y=e['center'];z=e['z']
 if id=='audio':return {'rotation':-90,'translation':[x-12.7,y+16.85,z]}
 return {'rotation':90,'translation':[x-1.80475,y-6.1114,z+.25]}
def transform_points(id,a):
 e=E[id];x,y=e['center'];z=e['z']
 if id=='audio':return np.column_stack((a[:,1]-12.7+x,-a[:,0]+16.85+y,a[:,2]+z))
 return np.column_stack((a[:,0]-1.80475+x,-a[:,2]-6.1114+y,a[:,1]+.25+z))
def vendor(id):
 src='6309.step' if id=='audio' else 'XIAO-ESP32S3 v2.step'
 s=cq.importers.importStep(str(ROOT.parent/'revision_04/vendor'/src));p=vendor_pose(id)
 axis=(0,0,1) if id=='audio' else (1,0,0)
 return s.rotate((0,0,0),axis,p['rotation']).translate(p['translation'])

def port_specs():
 # These points are extracted from the intact vendor CAD, transformed by the
 # SAME placement used for the whole board. They are not independent guesses.
 u=transform_points('xiao',np.array([[13.8086398,2.705,-6.1114]]))[0]
 j=transform_points('audio',np.array([[33.5370095,16.7591527,3.87248296]]))[0]
 sd=E['microsd'];sy=sd['center'][1];sz=sd['z']+1.55
 return {'usb':dict(edge='right',center=u.tolist(),width=9.4,height=3.7,axis=[1,0,0]),
         'jack':dict(edge='bottom',center=j.tolist(),diameter=5,axis=[0,-1,0]),
         'microsd':dict(edge='left',center=[-W/2+.4,sy,sz],width=11.5,height=1.5,axis=[-1,0,0])}

def side_slot(width,height,x,y,z,depth=8):
 return rounded(width,height,depth,min(.45,height/2-.01)).rotate((0,0,0),(1,1,1),120).translate((x-depth/2,y,z))
def port_tools():
 p=port_specs();u,j,s=p['usb'],p['jack'],p['microsd']
 tools={'usb':side_slot(u['width'],u['height'],W/2,u['center'][1],u['center'][2]),
 'microsd':side_slot(s['width'],s['height'],-W/2,s['center'][1],s['center'][2]),
 'jack':cyl(j['diameter']/2,8).rotate((0,0,0),(1,0,0),90).translate((j['center'][0],-L/2+4,j['center'][2]))}
 return tools

def ports(shape):
 for cutter in port_tools().values():shape=shape.cut(cutter)
 p=port_specs();u,j,s=p['usb'],p['jack'],p['microsd']
 # Blind enlarged connector pockets stop 1.0 mm short of the outside wall.
 shape=shape.cut(block(4,12,4.8,W/2-3,u['center'][1],u['center'][2]-2.4))
 shape=shape.cut(block(4,14.8,2.5,-W/2+3,s['center'][1],s['center'][2]-1.25))
 shape=shape.cut(block(8,4,6.2,j['center'][0],-L/2+3,j['center'][2]-3.1))
 return shape

def branding(shape):
 art=json.loads((ROOT.parent/'revision_04/assets/mytunas-branding.json').read_text())
 for key,width,cy in [('logo',18,8),('wordmark',22,-8)]:
  wires=[cq.Wire.makePolygon([cq.Vector(-x*width,y*width+cy,T-.25) for x,y in c[:-1]],close=True) for c in art[key]]
  wires.sort(key=lambda w:cq.Face.makeFromWires(w).Area(),reverse=True)
  for outer,*holes in sortWiresByBuildOrder(wires):shape=shape.cut(cq.Solid.extrudeLinear(cq.Face.makeFromWires(outer,holes),(0,0,.35)))
 return shape.clean()

def shells():
 def cavity(z,h):return rounded(W-3.2,L-3.2,h,4.4,z=z)
 front=rounded(W,L,B['front_height'],6).cut(cavity(1.2,8))
 front=front.cut(rounded(D['glass_size'][0]+.6,D['glass_size'][1]+.6,10,7.3,*D['center'],D['lip_z']))
 front=front.cut(rounded(*D['opening'],3,6.2,*D['center'],-1))
 start=B['front_height']+B['seam_gap']
 rear=rounded(W,L,T-start,6,z=start).cut(cavity(start-1,T-1.2-start+1))
 # Continuous overlapping seam with 0.2 mm clearance; not a waterproof seal.
 tongue=rounded(W-2.6,L-2.6,1.4,4.7,z=4.4).cut(rounded(W-4.4,L-4.4,2,3.8,z=4.2))
 front=front.union(tongue)
 groove=rounded(W-2.2,L-2.2,1.8,4.9,z=4.2).cut(rounded(W-4.8,L-4.8,2,3.6,z=4.1))
 rear=rear.cut(groove)
 # Connected corner screw towers, grown from front skin (no floating bosses).
 for x in [-F['x'],F['x']]:
  for y in F['y']:
   front=front.union(cyl(F['boss_radius'],F['mating_z']-1,x,y,1))
   front=front.cut(cyl(F['pilot_diameter']/2,8,x,y,F['pilot_bottom_z']))
   rear=rear.cut(cyl(F['boss_radius']+.2,F['mating_z']-start+.1,x,y,start-.1))
   rear=rear.union(cyl(F['boss_radius'],T-F['mating_z'],x,y,F['mating_z']))
   rear=rear.cut(cyl(F['clearance_diameter']/2,12,x,y,0)).cut(cyl(F['head_diameter']/2,3,x,y,F['head_seat_z']))
 # Exact DAC mounting-hole pads support the PCB underside; no pressure on chips.
 holes=transform_points('audio',np.array([[2.54,22.86,0],[29.21,2.54,0],[29.21,22.86,0]]))
 for x,y,z in holes:
  front=front.union(cyl(2,.6,x,y,1.2))
  front=front.union(cyl(.85,2.2,x,y,1.2))
  # Capture only the clear mounting-hole annulus, above the PCB face.
  rear=rear.union(cyl(1.85,T-1.2-3.57,x,y,3.57).cut(cyl(1.05,T,x,y,3.4)))
 # XIAO and SD underside lands end at PCB Z, connected to the front floor.
 for id in ['xiao','microsd']:
  e=E[id];x,y=e['center'];w,l,_=e['size']
  for sx in [-1,1]:
   for sy in [-1,1]:front=front.union(block(2,2,.6,x+sx*(w/2-2.2),y+sy*(l/2-2.2),1.2))
  # End stops oppose insertion forces. 0.3 mm lateral assembly clearance.
  stopx=x-w/2-.7 if id=='xiao' else x+w/2+.7
  front=front.union(block(.8,l-4,2.2,stopx,y,1.1))
 # Battery is in its own bay: foam below and guides outside the finished pack.
 b=P['battery'];x,y=b['center'];w,l,h=b['size']
 for sx in [-1,1]:front=front.union(block(.8,l+1,1.8,x+sx*(w/2+.8),y,1.1))
 for sy in [-1,1]:front=front.union(block(w+2,.8,1.8,x,y+sy*(l/2+.8),1.1))
 # A rear-removable open carrier spans the screen sides, never the glass
 # insertion path. Interface mounts on its four edge pads, above the ribbons.
 cy=D['center'][1]
 carrier=block(47.2,28,.6,0,cy,4.6).cut(block(45.6,24,1,0,cy,4.4))
 for sx in [-1,1]:
  # Seats are attached to the case walls but outside the glass sweep.
  front=front.union(block(1.6,28,.8,sx*24.0,cy,3.8))
  rear=rear.union(block(1.4,2,T-1.2-5.4,sx*22.8,cy+13,5.4))
 e=E['interface_pcb'];ex,ey=e['center'];ew,el,_=e['size']
 for yy in [ey-el/2+.8,ey+el/2-.8]:
  carrier=carrier.union(block(25.6,1.2,.6,10.8,yy,4.6))
  for xx in [ex-ew/2+.8,ex+ew/2-.8]:carrier=carrier.union(block(1.4,1.2,e['z']-5.2,xx,yy,5.2))
 return {'front_bezel':ports(front).clean(),'rear_shell':branding(ports(rear).clean()),'display_carrier':carrier.clean()}

# Visual subparts are real CAD solids; every one participates in assembly checks.
# Color subdivisions do not add a second overlapping outer box in the viewer.
def components():
 shapes={};visual={}
 def add(id,items):
  visual[id]=items;shapes[id]=compound([s for _,s in items])
 x,y=D['center'];z=D['glass_z'];gw,gl,gh=D['glass_size']
 add('touch_glass',[('#101b20',rounded(gw,gl,gh,7,x,y,z))])
 add('touch_sensor',[('#263d40',rounded(gw,gl,.7,7,x,y,z+.25))])
 ring=rounded(42,35,.2,6.5,x,y,D['lcd_z']-.2).cut(rounded(40,33,1,5.5,x,y,D['lcd_z']-.4))
 add('touch_lcd_tape',[('#ae8c44',ring)])
 add('lcd',[('#b4bdc1',rounded(42,35,2.15,6.5,x,y,D['lcd_z']))])
 seal=rounded(gw,gl,.2,7,x,y,D['lip_z']).cut(rounded(*D['opening'],1,6.2,x,y,D['lip_z']-.1))
 add('display_adhesive',[('#394448',seal)])
 for id in ['xiao','audio']:shapes[id]=vendor(id)
 b=P['battery'];x,y=b['center'];w,l,h=b['size'];z=b['z']
 pouch=rounded(w,l,h,.9,x,y,z)
 # Separate gold protection tape layer stays within the total 5 mm allowance.
 add('battery',[('#bfc6c6',pouch.cut(block(w+1,4,.12,x,y+l/2-2,z+h-.12))),('#d9a633',block(w-.5,3.8,.12,x,y+l/2-2,z+h-.12))])
 add('battery_foam',[('#383c3d',rounded(w-2,l-2,.6,.8,x,y,1.2))])
 e=E['microsd'];x,y=e['center'];z=e['z'];w,l,_=e['size']
 pcb=rounded(w,l,.8,.5,x,y,z)
 cage=block(15.5,14,1.8,-W/2+9,y,z+.8).cut(block(16,13,1.5,-W/2+8.5,y,z+.85))
 card=block(15,11,1,-W/2+.4+7.5,y,z+1.05)
 add('microsd',[('#256250',pcb),('#b1b9c0',cage),('#252b2d',card)])
 e=E['interface_pcb'];add('interface_pcb',[('#285c51',rounded(*e['size'],.4,*e['center'],e['z']))])
 for id,n,pitch in [('display_zif',15,.3),('touch_zif',6,.5)]:
  e=E[id];x,y=e['center'];w,l,h=e['size'];z=e['z']
  housing=block(w,l,h,x,y,z).cut(block(2.8,l-1,.3,x+1,y,z+.65))
  items=[('#252a2c',housing)]
  # Gold contacts end flush with the housing; slot opens toward +X.
  for i in range(n):items.append(('#cdaa50',block(2,.12,.05,x+.6,y+(i-(n-1)/2)*pitch,z+.65)))
  add(id,items)
 e=E['control'];x,y=e['center'];z=e['z']
 add('control',[('#242a2d',block(4,4,1.1,x,y,z)),('#a18b68',block(2,1.4,.8,x,y+3,z+.3)),('#a18b68',block(2,1.4,.8,x,y-3,z+.3))])
 # Proposed right-side folds. True finite-thickness solids, not decorative tubes.
 # Half annulus in XZ, extruded along Y. Straight legs meet tangent to the bend.
 for id,yy,width in [('display_flex',D['center'][1]+2,4.5),('touch_flex',D['center'][1]-6,3.0)]:
  cx=21.0;cz=D['lcd_z']+D['lcd_size'][2]+1.55;ro=1.55;ri=1.45
  bend=cq.Workplane('XZ').center(cx,cz).circle(ro).circle(ri).extrude(width).translate((0,yy+width/2,0))
  bend=bend.intersect(block(3,10,6,cx+1.5,yy,2))
  bottom=block(cx-19.8,width,.1,(cx+19.8)/2,yy,cz-ro)
  top=block(cx-16.5,width,.1,(cx+16.5)/2,yy,cz+ri)
  add(id,[('#bf841e' if id=='display_flex' else '#4e5041',bend.union(bottom).union(top))])
 # Screws shown at their true assembled coordinates. Thread major diameter
 # would interfere intentionally with polymer; model the 1.25 mm root diameter
 # and report nominal M1.6 thread as a fastening specification, not a solid fit.
 screws=[]
 for x in [-F['x'],F['x']]:
  for y in F['y']:
   screw=cyl(.625,F['screw_length'],x,y,F['head_seat_z']-F['screw_length']).union(cyl(1.5,.9,x,y,F['head_seat_z']))
   screw=screw.cut(block(2,.45,.4,x,y,F['head_seat_z']+.6)).cut(block(.45,2,.4,x,y,F['head_seat_z']+.6))
   screws.append(('#969ea4',screw))
 add('case_screws',screws)
 return shapes,visual
