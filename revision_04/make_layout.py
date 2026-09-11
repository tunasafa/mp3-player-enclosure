"""Draw P04 component and routing allocations directly from parameters.json."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
BASELINE=json.loads((ROOT/'layout_baseline.json').read_text())
BG,INK,MUTED='#f5f4f0','#182a34','#5c6d75'

def box(ax,center,size,color,label='',edge=None,dashed=False,fontsize=8):
    x,y=center;w,h=size
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0,rounding_size=.6',
                 facecolor=color,edgecolor=edge or color,lw=.9,linestyle='--' if dashed else '-'))
    if label:ax.text(x,y,label,ha='center',va='center',fontsize=fontsize,color=INK,linespacing=1.5)

def body(ax,title,previous=False):
    b=P['body']
    length,width=BASELINE['outer_length_width_thickness_mm'][:2] if previous else (b['length'],b['width'])
    box(ax,(0,0),(width,length),'#e4e8e3',edge='#81968c')
    ax.set(xlim=(-45,45),ylim=(-73,76),aspect='equal');ax.axis('off');ax.set_title(title,fontsize=12,pad=12)
    if not previous:
        for x in [-P['fasteners']['x'],P['fasteners']['x']]:
            for y in P['fasteners']['y']:ax.add_patch(Circle((x,y),3.2,fill=False,edgecolor=MUTED,lw=.8))

def rear_parts(ax, components):
    labels={'fpc8':'WHEEL FPC', 'xiao':'XIAO', 'dac':'TLV320\nDAC + JACK', 'microsd':'microSD',
            'battery_envelope':'503040\n600 mAh'}
    for key, part in components.items():
        if key not in labels:continue
        color='#d8af55' if key=='battery_envelope' else '#998fae' if key=='dac' else '#7fa79a'
        w,h=part['size'][:2]
        box(ax,part['center'],(w,h),color,f'{labels[key]}\n{w:g} × {h:g}',fontsize=7)

def main():
    fig=plt.figure(figsize=(16.5,10),facecolor=BG)
    fig.text(.045,.945,'MYTUNAS / COMPACT REPACK',fontsize=24,color=INK,weight='bold')
    b=P['body'];old=BASELINE['outer_length_width_thickness_mm']
    reduction=100*(1-b['length']*b['width']/(old[0]*old[1]))
    fig.text(.045,.91,f"{old[0]:g} × {old[1]:g} → {b['length']:g} × {b['width']:g} mm · depth {old[2]:g} → {b['thickness']:g} mm · same scale in all views",fontsize=12,color=MUTED)
    front=fig.add_axes([.015,.16,.245,.67]);body(front,'FRONT / REPACKED')
    d,q=P['display'],P['wheel']
    box(front,d['center'],d['size'][:2],'#9fb7bd','LANDSCAPE LCD\n52 × 40 body assumption')
    box(front,q['center'],q['backing'][:2],'none',edge='#81968c',dashed=True)
    front.add_patch(Circle(q['center'],q['face_diameter']/2,facecolor='#f3f1e7',edgecolor='#81968c'))
    front.text(*q['center'],'4TH-GEN WHEEL\nØ44 face assumption',ha='center',va='center',fontsize=9,linespacing=1.5)
    front.text(0,-64,'56 × 58 mm wheel backing\n1 mm to LCD body',ha='center',fontsize=8,color=MUTED,linespacing=1.6)
    before=fig.add_axes([.27,.16,.245,.67]);body(before,'REAR LAYER / BEFORE',True)
    rear_parts(before,BASELINE['components'])
    rear=fig.add_axes([.525,.16,.245,.67]);body(rear,'REAR LAYER / REPACKED')
    boards={e['id']:e for e in P['electronics']}
    rear_parts(rear,dict(boards,battery_envelope=P['battery']))
    for r in P['routing_reserves']:
        box(rear,r['center'],r['size'][:2],'none',edge='#4d90a1',dashed=True)
    jack_x=boards['dac']['center'][0]+P['ports']['jack']['axis_offset_x']
    rear.annotate('EARPHONES',xy=(jack_x,b['length']/2),xytext=(jack_x,b['length']/2+8),ha='center',fontsize=7,arrowprops={'arrowstyle':'-','color':MUTED})
    for key,label in [('xiao','USB'),('microsd','SD')]:
        y=boards[key]['center'][1]
        rear.annotate(label,xy=(b['width']/2,y),xytext=(42,y),ha='center',va='center',fontsize=7,arrowprops={'arrowstyle':'-','color':MUTED})
    fig.text(.79,.78,'LESS ENCLOSURE',fontsize=11,color='#0b756d',weight='bold')
    fig.text(.79,.73,f'{reduction:.1f}% less area',fontsize=20,color=INK,weight='bold')
    fig.text(.79,.68,f"{old[0]-b['length']:g} mm shorter, {old[1]-b['width']:g} mm narrower.\nSame screen, wheel and boards.\nSame 600 mAh battery.",fontsize=10,color=MUTED,linespacing=1.6,va='top')
    fig.text(.79,.54,'REPACKED REAR LAYER',fontsize=11,color='#0b756d',weight='bold')
    fig.text(.79,.49,'Cell entirely below the LCD.\nDAC flipped at upper left, USB right.\nFPC and card below the battery.\nFlush headphone socket at top.',fontsize=10,color=MUTED,linespacing=1.6,va='top')
    fig.text(.79,.32,'THINNER / SAME FOOTPRINT',fontsize=11,color='#0b756d',weight='bold')
    fig.text(.79,.27,f"{b['thickness']:g} mm shell depth, 0.2 mm less.\n1.0 mm local LCD seat floor.\n1.7 mm battery rear allowance retained.\nPhysical fit still unverified.",fontsize=10,color=MUTED,linespacing=1.6,va='top')
    fig.text(.045,.10,'All views look through the front. Dashed blue regions reserve harness/connector space, not verified cable routes.',fontsize=10,color=MUTED)
    fig.text(.045,.06,'FIT PROTOTYPE · exact modules, flex bends, mounting lands and battery maximum dimensions still need physical samples.',fontsize=10,color=INK)
    fig.savefig(ROOT/'internal_layout.png',dpi=180,facecolor=BG);plt.close(fig)
    print('Created P04 internal_layout.png')

if __name__=='__main__':main()
