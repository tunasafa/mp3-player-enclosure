"""Original vector tuna mark and outlined lettering, shared by SVG and CAD."""
from pathlib import Path
import json, os
os.environ.setdefault('MPLCONFIGDIR','/tmp/mytunas-matplotlib')
import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parent
def normalize(curves):
 a=np.concatenate(curves);lo=a.min(axis=0);hi=a.max(axis=0)
 return [np.round((c-(lo+hi)/2)/(hi[0]-lo[0]),6).tolist() for c in curves]
def text(s):return normalize(TextPath((0,0),s,size=100,prop=FontProperties(family='DejaVu Sans',weight='normal')).to_polygons())
# Torpedo body, swept dorsal fin, narrow peduncle and deeply forked caudal fin.
# The eye and swept pectoral slash are negative space, not raster decorations.
outer=np.array([[13,0],[9,2.7],[4,3.9],[0,4],[-3,7],[-2.4,3.6],[-6,2],[-8,.7],[-12,5],[-10.6,0],[-12,-5],[-8,-.7],[-5,-2.3],[0,-3.6],[4,-3.7],[2,-5.4],[7,-2.8],[10,-1.7],[13,0]],float)
eye=np.array([[8,1.35],[9.1,.8],[8.2,.15],[8,1.35]])
slash=np.array([[4,1.9],[-3,-1.2],[.3,-1],[4,1.9]])
art={'logo':normalize([outer,eye,slash]),'wordmark':text('mytunas'),'model':text('MODEL MT-02 / REV 03'),'type':text('DUAL CELL / TOUCH AUDIO'),'status':text('ENGINEERING PROTOTYPE'),'design':text('DESIGN M02-03 / 2026')}
data={'name':'mytunas bluefin','coordinates':'viewed face: X right, Y up; each group width normalized to 1','typeface':'DejaVu Sans, outlined','art':art,
 'front':[{'key':'logo','width':22,'cy':-15},{'key':'wordmark','width':23,'cy':-27}],
 'rear':[{'key':'logo','width':15,'cy':12},{'key':'wordmark','width':17,'cy':0},{'key':'model','width':27,'cy':-39},{'key':'type','width':28,'cy':-43},{'key':'status','width':28,'cy':-47},{'key':'design','width':25,'cy':-51}],
 'depth_mm':.03,'finish':'dark laser engraving in satin polished stainless; no regulatory certification symbols'}
(ROOT/'assets/branding.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
for face in ['front','rear']:
 paths=[]
 for spec in data[face]:
  for curve in art[spec['key']]:
   pts=np.array(curve)*spec['width'];pts[:,1]+=spec['cy']
   paths.append('M '+' L '.join(f'{x:.5f},{-y:.5f}' for x,y in pts)+' Z')
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-32 -64 64 128"><title>mytunas {face} engraving, millimetres</title><path fill="#244658" fill-rule="evenodd" d="{" ".join(paths)}"/></svg>\n'
 (ROOT/f'assets/{face}_engraving.svg').write_text(svg)
print('Created original vector tuna mark and front/rear engraving contours')
