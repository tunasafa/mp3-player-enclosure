"""Dimensioned nominal layout and thickness drawing, derived from parameters."""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/mytunas-matplotlib')
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
V=json.loads((ROOT/'validation.json').read_text())
B=P['body'];W,L,T=B['width'],B['length'],B['thickness']
fig=plt.figure(figsize=(14,10),facecolor='#f4f6f3')
grid=fig.add_gridspec(2,3,height_ratios=[4,1.5],left=.055,right=.97,bottom=.08,top=.84,wspace=.32,hspace=.3)
ink='#233e39';muted='#61796f'

def rect(ax,x,y,w,h,color,alpha=1,label=None):
    ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor=color,edgecolor=ink,lw=.8,alpha=alpha))
    if label: ax.text(x,y,label,ha='center',va='center',fontsize=7,color=ink)

def body(ax,title):
    ax.add_patch(FancyBboxPatch((-W/2,-L/2),W,L,boxstyle=f'round,pad=0,rounding_size={B["corner_radius"]}',fc='#d6e2dc',ec=ink,lw=1.2))
    ax.set(xlim=(-W/2-6,W/2+6),ylim=(-L/2-7,L/2+8),aspect='equal')
    ax.axis('off');ax.set_title(title,loc='left',fontsize=11,color=ink,pad=14)

def dim(ax,a,b,text,offset=(0,0)):
    ax.annotate('',xy=a,xytext=b,arrowprops={'arrowstyle':'|-|','lw':.8,'color':muted})
    ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],text,ha='center',va='center',fontsize=8,color=ink)

ax=fig.add_subplot(grid[0,0]);body(ax,'01 / FRONT — no wheel')
d=P['display'];x,y=d['center'];gw,gh,_=d['glass_size']
ax.add_patch(FancyBboxPatch((x-gw/2,y-gh/2),gw,gh,boxstyle='round,pad=0,rounding_size=3',fc='#172f2b',ec=ink))
aw,ah=V['derived']['active_area_mm'];rect(ax,x,y,aw,ah,'#6d9d86')
ax.text(x,y+4,'2.01-inch\n240 × 296',ha='center',va='center',fontsize=12,color='#f5faed')
ax.text(x,y-11,'touch UI',ha='center',fontsize=8,color='#e6f1df')
ax.text(0,-28,'mytunas',ha='center',fontsize=13,color=muted)
dim(ax,(-W/2,-L/2-4),(W/2,-L/2-4),f'{W} mm',(0,-2))
dim(ax,(-W/2-4,-L/2),(-W/2-4,L/2),f'{L}',(-2,0))
ax.text(0,L/2+4,f'Glass {gw:g} × {gh:g} mm ALLOWANCE',ha='center',fontsize=8,color=muted)

ax=fig.add_subplot(grid[0,1]);body(ax,'02 / PACKING — rear removed')
rect(ax,*d['center'],*d['glass_size'][:2],'#b8c8c0',.5)
b=P['battery'];rect(ax,*b['center'],*b['size'][:2],'#e2cf93',label='PROTECTED BATTERY\n34 × 30 × 3.4\ncapacity unspecified')
for e in P['electronics']:
    if e['id'] in ['control','display_zif','touch_zif']: color='#769b92'
    else: color={'xiao':'#70a98b','audio':'#c6a47a','microsd':'#b6c6cb'}.get(e['id'],'#87b29f')
    label={'xiao':'XIAO\nESP32-S3','audio':'AUDIO + JACK\nallowance','interface_pcb':'','microsd':'microSD','control':'I/O','display_zif':'LCD ZIF?','touch_zif':'TOUCH ZIF?'}.get(e['id'],e['id'])
    rect(ax,*e['center'],*e['size'][:2],color,label=label)
for sx in (-1,1):
    for y in P['fasteners']['y']:ax.add_patch(Circle((sx*P['fasteners']['x'],y),2,fc='#e7ece7',ec=ink,lw=.7))
ax.text(0,-L/2-4,'USB-C                  3.5 mm',ha='center',fontsize=8,color=ink)
ax.text(W/2+2,-9,'SD →',ha='left',fontsize=7,color=ink)

ax=fig.add_subplot(grid[0,2]);ax.set_title('03 / THICKNESS — allocations',loc='left',fontsize=11,color=ink,pad=14)
ax.set(xlim=(-2,20),ylim=(T+2,-1));ax.axis('off')
stacks=[(0,7,'SCREEN + BATTERY',[(d['glass_z'],d['glass_size'][2],'CG','#72968b'),(d['glass_z']+d['glass_size'][2],d['sensor_thickness'],'Sensor','#90b1a0'),(d['lcd_z']-d['tape_thickness'],d['tape_thickness'],'Tape','#d3bd85'),(d['lcd_z'],d['lcd_size'][2],'LCD','#829796'),(b['z']-.8,.6,'Tray','#88a995'),(b['z'],b['size'][2],'Battery','#e2cf93'),(b['z']+b['size'][2],1.7,'Free reserve','#f3e8cd'),(T-B['skin'],B['skin'],'Rear skin','#a1b7ad')]),(10,7,'LOWER AUDIO',[(0,1.2,'Front skin','#a1b7ad'),(3.4,5.2,'Audio + jack','#c6a47a'),(T-B['skin'],B['skin'],'Rear skin','#a1b7ad')])]
for x,w,title,layers in stacks:
    ax.text(x+w/2,-.4,title,ha='center',fontsize=8,color=muted)
    for z,h,label,color in layers:
        ax.add_patch(Rectangle((x,z),w,h,fc=color,ec=ink,lw=.7))
        ax.text(x+w/2,z+h/2,f'{label}\n{h:g} mm' if h>=1.2 else f'{label} {h:g}',ha='center',va='center',fontsize=5.5 if h<.4 else 7,color=ink)
dim(ax,(18.5,0),(18.5,T),f'{T}',(1.1,0))
ax.text(0,T+.7,f'Z=0 front → Z={T:g} rear\n0.2 mm LCD-to-tray gap; 2.0 mm battery rear gap.',fontsize=8,color=muted)

ax=fig.add_subplot(grid[1,:]);ax.axis('off')
texts=[('43% less footprint / 12% thinner','Compared with P04: 115 × 60 × 12.9 mm.\nBounding-box volume reduced by 50%.\nTwo shells + removable 0.6 mm battery tray.'),('CAD PASS / nominal geometry','Watertight, connected printed parts; exact XIAO.\nNo component or reserved-space intersections.\nFour M1.6 × 5 screws; test polymer thread fit.'),('MEASURE BEFORE FINAL FABRICATION','User layer estimates; outer glass unverified.\nCustom interface/audio PCB allowances required.\nSPI plausible; pin order and driver still unknown.')]
for i,(title,bodytext) in enumerate(texts):
    x=i/3;ax.text(x,.9,title,fontsize=10,weight='bold',color=ink,transform=ax.transAxes)
    ax.text(x,.72,bodytext,fontsize=9,color=muted,linespacing=1.8,va='top',transform=ax.transAxes)
fig.text(.055,.94,'mytunas / touch',fontsize=28,color=ink)
fig.text(.055,.90,f'MODEL 02     /     T01 CONDITIONAL FIT CONCEPT     /     {L:g} × {W:g} × {T:g} mm',fontsize=11,color=muted)
fig.text(.055,.035,'Millimetres. Drawings derived from parameters.json. Not a wiring diagram or certified component drawing.',fontsize=8,color=muted)
fig.savefig(ROOT/'design_overview.png',dpi=180,facecolor=fig.get_facecolor())
fig.savefig(ROOT/'design_overview.pdf',facecolor=fig.get_facecolor())
print('Wrote dimensioned PNG and PDF')
