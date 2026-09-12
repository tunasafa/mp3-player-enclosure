"""Dimensioned drawings from validated T02 bounds, not hand-positioned boxes."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/mytunas-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,Rectangle,Circle
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'parameters.json').read_text());v=json.loads((ROOT/'validation.json').read_text())
if not v['passed']:raise RuntimeError('Validate geometry first')
b=p['body'];w,l,t=b['width'],b['length'],b['thickness'];ink='#253e39';muted='#657b72'
fig,axs=plt.subplots(1,3,figsize=(13,10),gridspec_kw={'width_ratios':[1,1,1.4]},facecolor='#f3f5f0')
fig.subplots_adjust(left=.04,right=.96,top=.85,bottom=.15,wspace=.34)
def body(ax,title):
 ax.add_patch(FancyBboxPatch((-w/2,-l/2),w,l,boxstyle='round,pad=0,rounding_size=6',fc='#c2d0c9',ec=ink,lw=1))
 ax.set(xlim=(-w/2-10,w/2+10),ylim=(-l/2-10,l/2+8),aspect='equal');ax.axis('off');ax.set_title(title,loc='left',fontsize=11,color=ink,pad=20)
def rect(ax,bounds,color,label=None):
 a,b=bounds;x,y=a[:2];ww,hh=b[0]-x,b[1]-y
 ax.add_patch(Rectangle((x,y),ww,hh,fc=color,ec=ink,lw=.6))
 if label:ax.text(x+ww/2,y+hh/2,label,ha='center',va='center',fontsize=7,color=ink)
def dim(ax,a,b,text):
 ax.annotate('',xy=a,xytext=b,arrowprops={'arrowstyle':'|-|','color':muted,'lw':.8})
 ax.text((a[0]+b[0])/2,(a[1]+b[1])/2-3,text,ha='center',fontsize=8,color=ink)
a=axs[0];body(a,'01 / FRONT')
d=p['display'];x,y=d['center'];gw,gl,_=d['glass_size']
a.add_patch(FancyBboxPatch((x-gw/2,y-gl/2),gw,gl,boxstyle='round,pad=0,rounding_size=7',fc='#142e2d',ec=ink))
a.text(x,y,'LANDSCAPE\n296 × 240',color='#cbe4cb',fontsize=10,ha='center',va='center')
a.text(0,-23,'mytunas',fontsize=13,color=muted,ha='center')
dim(a,(-w/2,-l/2-5),(w/2,-l/2-5),f'{w} mm')
a.text(-w/2-7,0,f'{l} mm',rotation=90,va='center',fontsize=8,color=ink)
a.text(0,l/2+3,'43 × 36 mm outer glass',ha='center',fontsize=8,color=ink)
a=axs[1];body(a,'02 / PACKING — front-coordinate plan')
for id,col,lab in [('lcd','#9caaa6','LCD / backlight'),('xiao','#789e8b','XIAO\nESP32-S3'),('microsd','#a7b6b9','microSD'),('battery','#ddca8c','503040 LiPo\n40 × 30 × 5'),('audio','#a59eae','INTACT ADAFRUIT\nTLV320DAC3100')]:rect(a,v['cad_parts'][id]['bounds_mm'],col,lab)
for r in p['routing_reserves']:
 if r['id']=='battery_expansion':continue
 x,y=r['center'];rw,rl,_=r['size'];a.add_patch(Rectangle((x-rw/2,y-rl/2),rw,rl,fill=False,ec='#ab753d',lw=.8,ls='--'))
for x in [-p['fasteners']['x'],p['fasteners']['x']]:
 for y in p['fasteners']['y']:a.add_patch(Circle((x,y),2.2,fc='#e6eae3',ec=ink,lw=.6))
for name,port in v['ports'].items():
 x,y,z=port['center'];a.plot(x,y,'o',ms=3,color='#24675c')
 if name=='jack':a.annotate('3.5 mm JACK',xy=(x,y),xytext=(0,y-7),ha='center',fontsize=7,arrowprops={'arrowstyle':'->','color':ink})
 else:a.annotate('USB-C' if name=='usb' else 'SD',xy=(x,y),xytext=(x+(6 if x>0 else -6),y+5),ha='center',fontsize=7,arrowprops={'arrowstyle':'->','color':ink})
a=axs[2];a.axis('off');a.set_title('03 / THICKNESS LIMIT',loc='left',fontsize=11,color=ink,pad=20)
y=.95
for title,text in [
 ('10.4 mm practical target','1.2 mm front skin\n0.6 mm board mounting height\n7.1 mm full Adafruit product height\n0.3 mm rear clearance\n1.2 mm rear skin'),
 ('Separate battery bay','5 mm nominal protected pack\n2.4 mm to the rear skin\n1.7 mm of that reserved clear'),
 ('Port alignment','USB right · SD left · headphones bottom\nActual board transforms set USB/jack axes\nBlind pockets retain a 1 mm outer lip'),
 ('Strict nominal checks',f"{len(v['collisions'])} assembly collisions\n{len(v['reserve_collisions'])} reserved-space collisions\nConnected, watertight shell / carrier meshes"),
 ('Physical fit still required','Panel border and folded ribbons estimated\nSD assembly and interface PCB provisional\nUnsealed ports; no water/dust rating')]:
 a.text(0,y,title,fontsize=12,color=ink,weight='bold',va='top',transform=a.transAxes)
 a.text(0,y-.04,text,fontsize=9,color=muted,linespacing=1.7,va='top',transform=a.transAxes)
 y-=.245 if title.startswith('10.4') else .18
fig.text(.05,.94,'mytunas / touch',fontsize=27,color=ink)
fig.text(.05,.90,f'T02 / BATTERY ABOVE DAC / BOTTOM JACK / {w} × {l} × {t} mm',fontsize=11,color=muted)
fig.text(.05,.075,'Same parts and coordinates as the STEP assembly and interactive viewer. All dimensions in millimetres.',fontsize=9,color=muted)
fig.text(.05,.05,'Prototype: sample measurements, flex folding, PCB selection and a physical fit test remain necessary.',fontsize=9,color=muted)
for ext in ['png','pdf']:fig.savefig(ROOT/f'design_overview.{ext}',dpi=170,facecolor=fig.get_facecolor())
print('Wrote T02 dimensioned drawings')
