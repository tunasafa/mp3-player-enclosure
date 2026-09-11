"""Draw P04 component and routing allocations directly from parameters.json."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
BG,INK,MUTED='#f5f4f0','#182a34','#5c6d75'

def box(ax,center,size,color,label='',edge=None,dashed=False,fontsize=8):
    x,y=center;w,h=size
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0,rounding_size=.6',
                 facecolor=color,edgecolor=edge or color,lw=.9,linestyle='--' if dashed else '-'))
    if label:ax.text(x,y,label,ha='center',va='center',fontsize=fontsize,color=INK,linespacing=1.5)

def body(ax,title):
    b=P['body'];box(ax,(0,0),(b['width'],b['length']),'#e4e8e3',edge='#81968c')
    ax.set(xlim=(-45,45),ylim=(-73,76),aspect='equal');ax.axis('off');ax.set_title(title,fontsize=12,pad=12)
    for x in [-P['fasteners']['x'],P['fasteners']['x']]:
        for y in P['fasteners']['y']:ax.add_patch(Circle((x,y),3.2,fill=False,edgecolor=MUTED,lw=.8))

def main():
    fig=plt.figure(figsize=(15,10),facecolor=BG)
    fig.text(.055,.945,'FORM 04 / COMPONENT LAYOUT',fontsize=24,color=INK,weight='bold')
    fig.text(.055,.91,'134 × 72 × 13.4 mm · all positions viewed through the front · millimetres',fontsize=12,color=MUTED)
    front=fig.add_axes([.035,.16,.3,.67]);body(front,'FRONT INTERFACE')
    d,q=P['display'],P['wheel']
    box(front,d['center'],d['size'][:2],'#9fb7bd','LANDSCAPE LCD\n52 × 40 body assumption')
    box(front,q['center'],q['backing'][:2],'none',edge='#81968c',dashed=True)
    front.add_patch(Circle(q['center'],q['face_diameter']/2,facecolor='#f3f1e7',edgecolor='#81968c'))
    front.text(*q['center'],'4TH-GEN WHEEL\nØ44 face assumption',ha='center',va='center',fontsize=9,linespacing=1.5)
    front.text(0,-47,'Complete backing: 56 × 58 assumed',ha='center',fontsize=8,color=MUTED)
    rear=fig.add_axes([.35,.16,.3,.67]);body(rear,'REAR COMPONENT ALLOCATION')
    b=P['battery'];box(rear,b['center'],b['size'][:2],'#d8af55','503040 BATTERY\n600 mAh\n40 × 30 × 5')
    labels={'fpc8':'WHEEL FPC\n26.1 × 19.1','xiao':'XIAO\n21 × 17.8',
            'dac':'TLV320DAC3100\nDAC + HEADPHONE\n25.4 × 33.7\n7.1 thick','microsd':'microSD\n22 × 18'}
    for e in P['electronics']:
        color='#998fae' if e['id']=='dac' else '#7fa79a'
        box(rear,e['center'],e['size'][:2],color,labels[e['id']],fontsize=7.7)
    for r in P['routing_reserves']:
        box(rear,r['center'],r['size'][:2],'none',edge='#4d90a1',dashed=True)
    rear.annotate('EARPHONES',xy=(4.059,67),xytext=(4.059,73),ha='center',fontsize=8,arrowprops={'arrowstyle':'-','color':MUTED})
    for y,label in [(-24,'USB'),(-46,'SD')]:
        rear.annotate(label,xy=(36,y),xytext=(42,y),ha='center',va='center',fontsize=7,arrowprops={'arrowstyle':'-','color':MUTED})
    fig.text(.69,.78,'CLEARANCE CORRECTION',fontsize=11,color='#0b756d',weight='bold')
    fig.text(.69,.73,'0.35 → 2.85 mm',fontsize=24,color=INK,weight='bold')
    fig.text(.69,.68,'Clickwheel breakout to the left wall.\nMoved 2.5 mm inward and 11.5 mm down.',fontsize=10,color=MUTED,linespacing=1.6,va='top')
    fig.text(.69,.57,'SMALLER BATTERY',fontsize=11,color='#0b756d',weight='bold')
    fig.text(.69,.52,'600 mAh / 2.22 Wh nominal',fontsize=16,color=INK)
    fig.text(.69,.46,'30% of the previous 2000 mAh capacity.\n5 mm listed thickness; finished pack unmeasured.\n2.0 mm nominal gap to rear skin.',fontsize=10,color=MUTED,linespacing=1.6,va='top')
    fig.text(.69,.34,'ONE OUTPUT OPENING',fontsize=11,color='#0b756d',weight='bold')
    fig.text(.69,.29,'DAC moved behind the LCD, jack toward the top.\n0.3 mm modeled gap on each side of its depth.\nIntegrated amplifier drives passive earphones.',fontsize=10,color=MUTED,linespacing=1.6,va='top')
    fig.text(.055,.10,'Dashed blue volumes reserve harness/connector space. They may join; they are not measured cable routes.',fontsize=10,color=MUTED)
    fig.text(.055,.06,'FIT PROTOTYPE · module variants, socket axis, flex bend radii, mounting lands and battery maximum dimensions remain provisional.',fontsize=10,color=INK)
    fig.savefig(ROOT/'internal_layout.png',dpi=180,facecolor=BG);plt.close(fig)
    print('Created P04 internal_layout.png')

if __name__=='__main__':main()
