"""Dimensioned engineering reference set from the current validated assembly."""
from pathlib import Path
import json,csv,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/mytunas-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle,FancyBboxPatch,Circle
from matplotlib.patches import PathPatch
from matplotlib.path import Path as PlotPath
ROOT=Path(__file__).resolve().parent
p=json.loads((ROOT/'parameters.json').read_text());v=json.loads((ROOT/'validation.json').read_text());data=json.loads((ROOT/'model.json').read_text())
assert v['passed'] and data['report']==v
ink='#24433f';muted='#637875';bg='#f3f5f3'
def page(title,subtitle):
 f=plt.figure(figsize=(11.7,8.3),facecolor=bg)
 f.text(.05,.94,title,fontsize=21,color=ink);f.text(.05,.9,subtitle,fontsize=9,color=muted)
 f.text(.05,.035,'M02-03 / mm / nominal mechanical prototype / do not scale PDF / no production release',fontsize=8,color=muted)
 return f
def body(ax):
 ax.add_patch(FancyBboxPatch((-32,-64),64,128,boxstyle='round,pad=0,rounding_size=6',facecolor='#dae3df',edgecolor=ink,lw=.8))
 ax.set(xlim=(-43,43),ylim=(-76,74),aspect='equal');ax.axis('off')
def dim(ax,a,b,label,vertical=False):
 ax.annotate('',xy=a,xytext=b,arrowprops={'arrowstyle':'|-|','color':muted,'lw':.7})
 ax.text((a[0]+b[0])/2+(-2 if vertical else 0),(a[1]+b[1])/2+(-3 if not vertical else 0),label,fontsize=8,rotation=90 if vertical else 0,ha='center',va='center',color=ink)
def rect(ax,id,color,label):
 a,b=v['cad_parts'][id]['bounds_mm'];x,y=a[:2];w,h=b[0]-x,b[1]-y
 ax.add_patch(Rectangle((x,y),w,h,fc=color,ec=ink,lw=.7));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=7,color=ink)
def table(ax,rows,columns,widths=None,size=9):
 ax.axis('off');t=ax.table(cellText=rows,colLabels=columns,cellLoc='left',colLoc='left',loc='upper left',colWidths=widths);t.auto_set_font_size(False);t.set_fontsize(size);t.scale(1,1.65)
 for (r,c),cell in t.get_celld().items():cell.set_edgecolor('#d0dad6');cell.set_facecolor('#dce7e0' if r==0 else bg);cell.set_text_props(color=ink)
 return t
with PdfPages(ROOT/'drawings.pdf') as pdf:
 f=page('mytunas / Model 02','01 — Exterior and internal arrangement. Front-coordinate plan; component rectangles show validated bounds.')
 a=f.add_axes([.04,.13,.24,.71]);body(a)
 x,y=p['display']['window_center'];w,h=p['display']['window'];a.add_patch(Rectangle((x-w/2,y-h/2),w,h,fc='#123039',ec=ink));a.text(x,y,'2.4-inch IPS\n320 × 240',ha='center',va='center',fontsize=10,color='white')
 dim(a,(-32,-70),(32,-70),'64.00');dim(a,(-38,-64),(-38,64),'128.00',True)
 art=json.loads((ROOT/'assets/branding.json').read_text())
 for spec in art['front']:
  paths=[]
  for curve in art['art'][spec['key']]:
   pts=[(x*spec['width'],y*spec['width']+spec['cy']) for x,y in curve]
   if spec['key']=='logo':
    signed=sum(pts[i][0]*pts[i+1][1]-pts[i+1][0]*pts[i][1] for i in range(len(pts)-1))
    if not paths:outer_sign=signed
    elif signed*outer_sign>0:pts=pts[::-1]
   paths.append(PlotPath(pts,[PlotPath.MOVETO]+[PlotPath.LINETO]*(len(pts)-2)+[PlotPath.CLOSEPOLY]))
  a.add_patch(PathPatch(PlotPath.make_compound_path(*paths),facecolor='#314655',lw=0))
 a=f.add_axes([.3,.13,.26,.71]);body(a)
 for id,col,label in [('lcd','#90a7a3','LCD / 60.26 × 42.92'),('display_carrier','#cad8d2',''),('microsd_pcb','#80a89b','SD'),('interface_pcb','#80a89b','45P I/O'),('cell_A_envelope','#d3c7a1','Cell A\n37 × 25.5'),('cell_B_envelope','#d3c7a1','Cell B\n25.5 × 37'),('audio','#96a8c1','Adafruit\n6309'),('xiao','#80a89b','XIAO')]:rect(a,id,col,label)
 for x,y in p['case_fasteners']['points']:a.add_patch(Circle((x,y),1.9,fc='white',ec=ink,lw=.6))
 for n,port in v['ports'].items():x,y,z=port['center'];a.plot(x,y,'o',ms=3,color='#236656');a.annotate(n,xy=(x,y),xytext=(x+(4 if x>=0 else -4),y-5),fontsize=7,ha='center')
 a=f.add_axes([.61,.2,.35,.63]);table(a,[['Body','64 × 128 × 8.30'],['Corner radius','R6.00'],['Steel faces','0.40 each'],['Frame perimeter','Z0.55 to 7.75'],['Rear hard stops','Z7.90 contact plane'],['Display opening','49.56 × 37.32'],['Display centre','X0, Y35'],['USB opening','9.24 × 3.51 / rim profile'],['Headphone opening','Diameter 5.00'],['SD opening','11.50 × 1.50'],['Covers','Flush / removable prototype']],['Feature','Dimension'],[.39,.61],8)
 f.savefig(ROOT/'design_overview.png',dpi=170,facecolor=bg);pdf.savefig(f);plt.close(f)
 f=page('Hole and port coordinates','02 — Datum: body centre X0/Y0; front exterior Z0. All dimensions in millimetres.')
 a=f.add_axes([.05,.12,.27,.72]);body(a)
 for i,(x,y) in enumerate(p['case_fasteners']['points'],1):a.add_patch(Circle((x,y),1.9,fill=False,ec=ink));a.text(x+(4 if x<0 else -4),y,str(i),fontsize=8,ha='center')
 for x,y in p['carrier']['screw_points']:a.plot(x,y,'+',color='#ad7247')
 rows=[[str(i),f'{x:.2f}',f'{y:.2f}','M1.6 × 5 / CSK'] for i,(x,y) in enumerate(p['case_fasteners']['points'],1)]
 rows += [[f'C{i}',f'{x:.2f}',f'{y:.2f}','M1.4 × 3 / carrier'] for i,(x,y) in enumerate(p['carrier']['screw_points'],1)]
 for i,(x,y) in enumerate(p['xiao_clamp']['screw_points'],1):
  a.plot(x,y,'x',color='#80643d');rows.append([f'X{i}',f'{x:.2f}',f'{y:.2f}','M1.4 × 3 / saddle'])
 for i in range(1,4):
  lo,hi=v['cad_parts'][f'dac_retainer_{i}']['bounds_mm'];x=(lo[0]+hi[0])/2;y=(lo[1]+hi[1])/2
  a.plot(x,y,'o',ms=2,color='#80643d');rows.append([f'D{i}',f'{x:.2f}',f'{y:.2f}','M1.4 × 3 / rear column'])
 t=table(f.add_axes([.36,.34,.58,.50]),rows,['ID','X','Y','Fastener'],[.12,.18,.18,.52],7.5);t.scale(1,.85)
 portrows=[[n,*[f'{c:.4f}' for c in port['center']]] for n,port in v['ports'].items()]
 table(f.add_axes([.36,.11,.58,.2]),portrows,['Mouth centre','X','Y','Z'],[.28,.24,.24,.24],8)
 pdf.savefig(f);plt.close(f)
 f=page('Depth sections and reserves','03 — Layer values are nominal allocations. Full published DAC height is retained.')
 stacks=[('DAC',[(0,.4,'Steel'),(.4,.55,'Insulation'),(.55,7.65,'Published DAC max'),(7.65,7.83,'Free 0.18'),(7.83,7.9,'Liner'),(7.9,8.3,'Steel')]),('Battery',[(0,.4,'Steel'),(.4,.7,'Adhesive'),(.7,5.9,'Pack max 5.20'),(5.9,7.6,'Expansion 1.70'),(7.6,7.83,'Free 0.23'),(7.83,7.9,'Liner'),(7.9,8.3,'Steel')]),('LCD + SD',[(0,.4,'Bezel'),(.4,.55,'Bond'),(.55,4.3,'Touch + LCD 3.75'),(4.3,4.35,'Cushion'),(4.35,4.55,'Carrier'),(4.55,4.85,'SD adhesive'),(4.85,7.45,'SD max'),(7.45,7.83,'Free 0.38'),(7.83,7.9,'Liner'),(7.9,8.3,'Steel')])]
 colors=['#92aaa2','#dcc28a','#8ca6b2','#bad3bd','#cba569','#92aaa2']
 for i,(title,layers) in enumerate(stacks):
  ax=f.add_axes([.08+i*.31,.18,.23,.65]);ax.set(xlim=(-.1,3.2),ylim=(8.6,-.3));ax.set_title(title,loc='left',fontsize=12,color=ink);ax.set_ylabel('Z / mm');ax.set_xticks([])
  for j,(lo,hi,label) in enumerate(layers):
   ax.add_patch(Rectangle((0,lo),1,hi-lo,fc=colors[j%len(colors)],ec=ink,lw=.4))
   label_y=(j+.5)*8.3/len(layers)
   ax.plot([1,1.12,1.25],[(lo+hi)/2,(lo+hi)/2,label_y],color=muted,lw=.5)
   ax.text(1.3,label_y,f'{lo:.2f}–{hi:.2f}\n{label}',fontsize=7,va='center',color=ink)
  ax.spines[['top','right','bottom']].set_visible(False)
 f.savefig(ROOT/'depth_sections.png',dpi=170,facecolor=bg);pdf.savefig(f);plt.close(f)
 f=page('Manufacturing and assembly checkpoints','04 — STEP defines 3D geometry. DXF profiles are for the named sheet layers only.')
 rows=[['Frame','PA12 / 13 metal threaded inserts','Use BEFORE_HEAT_INSERTS geometry'],['Front / rear','0.40 mm satin polished stainless','0.03 mm original vector engravings'],['Carrier','0.20 web / four 0.30 mm welded blades','Weld in flat fixture; inspect distortion'],['Case threads','7 × PEM MSIB-M1.6-300','Pilot 2.15 / depth 3.77 minimum'],['Internal threads','6 × PEM MSIB-M1.4-150','Pilot 2.15 / depth 2.27 minimum'],['XIAO saddle','0.40 steel / 0.30 shield cushion','Two M1.4 × 3 screws; qualify shield load'],['DAC retention','3 steel columns / insulated seats','Three rear M1.4 × 3 CSK screws'],['Ports','Actual USB rim + 0.15 radial gap','Positive clearance; optional covers'],['Release gate','0.18 mm DAC clearance is tight','Tolerance stack and physical cycle tests']]
 table(f.add_axes([.04,.21,.91,.64]),rows,['Part / check','Specification','Process note'],[.17,.39,.44],9)
 pdf.savefig(f);plt.close(f)
 # All physical-part bounds provide a complete measurement schedule.
 items=[part for part in data['parts'] if not part['reserve']]
 for page_start in range(0,len(items),20):
  f=page('Part measurement schedule',f'{5+page_start//20:02d} — Bounding dimensions and assembly position; holes and contours are defined by STEP.')
  rows=[]
  for part in items[page_start:page_start+20]:
   a,b=part['bounds_mm'];rows.append([part['id'],' × '.join(f'{b[i]-a[i]:.2f}' for i in range(3)),', '.join(f'{q:.2f}' for q in a)])
  table(f.add_axes([.04,.11,.92,.74]),rows,['Part','W × L × H','Minimum X, Y, Z'],[.38,.3,.32],8)
  pdf.savefig(f);plt.close(f)
with (ROOT/'measurements.csv').open('w',newline='') as fp:
 w=csv.writer(fp);w.writerow(['part','label','width_mm','length_mm','height_mm','xmin_mm','ymin_mm','zmin_mm','source'])
 for part in items:
  a,b=part['bounds_mm'];w.writerow([part['id'],part['label'],*[round(b[i]-a[i],5) for i in range(3)],*[round(q,5) for q in a],part['source']])
print('Wrote dimensioned multi-page PDF, overview and complete measurement CSV')
