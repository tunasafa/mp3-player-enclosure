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
  wires=[cq.Wire.makePolygon([cq.Vector(-x*width,y*width+cy,T-P['branding']['depth']) for x,y in c[:-1]],close=True) for c in art[key]]
  wires.sort(key=lambda w:cq.Face.makeFromWires(w).Area(),reverse=True)
  for outer,*holes in sortWiresByBuildOrder(wires):shape=shape.cut(cq.Solid.extrudeLinear(cq.Face.makeFromWires(outer,holes),(0,0,P['branding']['depth']+.1)))
 return shape.clean()

def screw_head(x,y,extra=0):
 return cq.Workplane('XY').newObject([cq.Solid.makeCone(.8+extra,1.6+extra,.8)]).translate((x,y,T-.8))

def shells():
 front=rounded(W,L,.4,6).cut(rounded(*D['opening'],2,6.2,*D['center'],-.5))
 rear=rounded(W,L,.4,6,z=T-.4)
 # One open polymer skeleton, bonded to the front face. Metal faces are
 # separate solids and separate manufacturing processes, never printed skins.
 frame=rounded(W,L,7.2,6,z=.55).cut(rounded(W-3.2,L-3.2,9,4.4,z=.4))
 for x in [-F['x'],F['x']]:
  for y in F['y']:
   frame=frame.union(cyl(2.2,7.2,x,y,.55))
   # Join middle bosses to the side walls rather than leave floating cylinders.
   frame=frame.union(block(3,3,7.2,math.copysign(W/2-2,x),y,.55))
   frame=frame.cut(cyl(.65,9,x,y,2.7)).cut(screw_head(x,y,.1))
   rear=rear.cut(cyl(.9,2,x,y,7)).cut(screw_head(x,y))
 # DAC edge guides react insertion load. The underside sits on insulation;
 # separate rear spacers locate and retain it through its real mounting holes.
 a=E['audio'];amin=a['center'][0]-12.7;amax=a['center'][0]+12.7;top=a['center'][1]+16.85
 for xx in [amin-.8,amax+.8]:
  frame=frame.union(block(1,top+L/2,2,xx,(-L/2+top)/2,.55))
 frame=frame.union(block(amax-amin+2.6,1,2,a['center'][0],top+.8,.55))
 # Headerless boards sit on dielectric pads. End stops capture port insertion.
 for id in ['xiao','microsd']:
  e=E[id];x,y=e['center'];w,l,_=e['size'];stopx=x-w/2-.7 if id=='xiao' else x+w/2+.7
  frame=frame.union(block(.8,l+1,1.8,stopx,y,.55))
  # Crossbars lie outside each PCB footprint and connect stops to side rails.
  sx=1 if id=='xiao' else -1;end=sx*(W/2-.8)
  for yy in [y-l/2-.6,y+l/2+.6]:frame=frame.union(block(abs(end-stopx)+.8,.8,1.8,(end+stopx)/2,yy,.55))
 # Battery guides tie into side rails below the cell; no material occupies
 # the 1.7 mm expansion reserve above it.
 b=P['battery'];bx,by=b['center'];bw,bl,_=b['size']
 for yy in [by-bl/2-.5,by+bl/2+.5]:frame=frame.union(block(W-2,.6,1.4,0,yy,.55))
 for xx in [-20.8,20.8]:frame=frame.union(block(.8,bl+2,1.4,xx,by,.55))
 # Screen shelf outside the glass insertion sweep; removable carrier above LCD.
 cx,cy=D['center']
 frame=frame.union(block(2.7,37,3.45,-29.05,cy,.55))
 frame=frame.union(block(1,42,3.45,16.6,43,.55))
 carrier=rounded(44,37,.4,7,cx,cy,4).cut(rounded(40,33,1,5,cx,cy,3.8))
 for yy in [22,61.4]:
  taby=yy if yy==22 else 61.1
  carrier=carrier.union(block(3,3.4 if yy==22 else 2.6,.4,cx,taby,4)).cut(cyl(.6,2,cx,yy,3.5))
  frame=frame.union(cyl(1.2,3.45,cx,yy,.55))
 frame=frame.union(block(25,.8,1.2,-18.3,22,.55))
 # Interface in a separate right-side bay, with corner lands under its PCB.
 e=E['interface_pcb'];ex,ey=e['center'];ew,el,_=e['size']
 for yy in [ey-el/2+.8,ey+el/2-.8]:
  frame=frame.union(block(13,1.2,.7,25,yy,.55))
  for xx in [ex-ew/2+.8,ex+ew/2-.8]:frame=frame.union(block(1.4,1.2,e['z']-.55,xx,yy,.55))
 # Recut after all unions: ribs must never refill a screw pilot.
 for x in [-F['x'],F['x']]:
  for y in F['y']:frame=frame.cut(cyl(.65,9,x,y,2.7)).cut(screw_head(x,y,.1))
 for yy in [22,61.4]:frame=frame.cut(cyl(.4,4,-6,yy,.7))
 for yy,ww in [(45,4.5),(37,3)]:frame=frame.cut(block(2,ww+.6,.5,16.6,yy,3.65))
 return {'front_bezel':front.clean(),'rear_shell':branding(rear),'midframe':ports(frame).clean(),'display_carrier':carrier.clean()}

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
 seal=rounded(gw,gl,.15,7,x,y,D['lip_z']).cut(rounded(*D['opening'],1,6.2,x,y,D['lip_z']-.1))
 add('display_adhesive',[('#394448',seal)])
 for id in ['xiao','audio']:shapes[id]=vendor(id)
 b=P['battery'];x,y=b['center'];w,l,h=b['size'];z=b['z']
 pouch=rounded(w,l,h,.9,x,y,z)
 # Separate gold protection tape layer stays within the total 5 mm allowance.
 add('battery',[('#bfc6c6',pouch.cut(block(w+1,4,.12,x,y+l/2-2,z+h-.12))),('#d9a633',block(w-.5,3.8,.12,x,y+l/2-2,z+h-.12))])
 add('battery_foam',[('#383c3d',rounded(w-2,l-2,.3,.8,x,y,.4))])
 e=E['microsd'];x,y=e['center'];z=e['z'];w,l,_=e['size']
 pcb=rounded(w,l,.8,.5,x,y,z)
 cage=block(15.5,14,1.8,-W/2+9,y,z+.8).cut(block(16,13,1.5,-W/2+8.5,y,z+.85))
 card=block(15,11,1,-W/2+.4+7.5,y,z+1.05)
 add('microsd',[('#256250',pcb),('#b1b9c0',cage),('#252b2d',card)])
 e=E['interface_pcb'];add('interface_pcb',[('#285c51',rounded(*e['size'],.4,*e['center'],e['z']))])
 for id,n,pitch in [('display_zif',15,.3),('touch_zif',6,.5)]:
  e=E[id];x,y=e['center'];w,l,h=e['size'];z=e['z']
  housing=block(w,l,h,x,y,z).cut(block(2.8,l-1,.3,x-1,y,z+.65))
  items=[('#252a2c',housing)]
  # Gold contacts end flush with the housing; slot opens toward +X.
  for i in range(n):items.append(('#cdaa50',block(2,.12,.05,x-.6,y+(i-(n-1)/2)*pitch,z+.65)))
  add(id,items)
 e=E['control'];x,y=e['center'];z=e['z']
 add('control',[('#242a2d',block(4,4,1.1,x,y,z)),('#a18b68',block(2,1.4,.8,x,y+3,z+.3)),('#a18b68',block(2,1.4,.8,x,y-3,z+.3))])
 # Side tails remain an explicit mechanical hypothesis from the photo.
 for id,yy,width in [('display_flex',45,4.5),('touch_flex',37,3.0)]:
  add(id,[('#bf841e' if id=='display_flex' else '#4e5041',block(7.1,width,.1,18.35,yy,3.85))])
 # Insulation and adhesive are represented as finite thickness solids.
 for id in ['audio','xiao','microsd']:
  e=E[id];x,y=e['center'];w,l,_=e['size']
  if id=='audio':l=31.75;y=e['center'][1]+16.85-l/2
  pad=block(w,l,e['z']-.4,x,y,.4)
  add(id+'_insulator',[('#b89240',pad)])
 # Perimeter bond rings provide actual metal/frame contact in the stack.
 for id,z,h in [('front_bond',.4,.15),('rear_gasket',7.75,.15)]:
  ring=rounded(W,L,h,6,z=z).cut(rounded(W-2.8,L-2.8,h+1,4.6,z=z-.2))
  for x in [-F['x'],F['x']]:
   for y in F['y']:ring=ring.cut(cyl(1.8,1,x,y,z-.2))
  add(id,[('#373e3e',ring)])
 # Nonconductive rear spacers seat on the manufacturer mounting-hole annuli.
 # Each has a locating pin entering the real PCB hole. They are separate parts,
 # held against the back plate; mechanical bonding must be qualified.
 holepoints=transform_points('audio',np.array([[2.54,22.86,0],[29.21,2.54,0],[29.21,22.86,0]]))
 spacers=[]
 for x,y,z in holepoints:
  spacer=cyl(1.85,T-.4-(z+1.57),x,y,z+1.57).union(cyl(.85,1.57,x,y,z))
  spacers.append(('#68766d',spacer))
 add('dac_retention',spacers)
 rearfilm=rounded(W-3.6,L-3.6,.07,4.2,z=T-.47)
 for x in [-F['x'],F['x']]:
  for y in F['y']:rearfilm=rearfilm.cut(cyl(1.9,1,x,y,T-1))
 for x,y,z in holepoints:rearfilm=rearfilm.cut(cyl(1.95,1,x,y,T-1))
 add('rear_liner',[('#b69751',rearfilm)])
 screws=[]
 for x in [-F['x'],F['x']]:
  for y in F['y']:
   screw=cyl(.625,4.2,x,y,T-5).union(screw_head(x,y))
   screw=screw.cut(block(2,.4,.3,x,y,T-.25)).cut(block(.4,2,.3,x,y,T-.25))
   screws.append(('#919a9f',screw))
 add('case_screws',screws)
 screws=[]
 for yy in [22,61.4]:
  screw=cyl(.35,2.9,-6,yy,1.5).union(cyl(.9,.5,-6,yy,4.4))
  screws.append(('#919a9f',screw))
 add('carrier_screws',screws)
 return shapes,visual
