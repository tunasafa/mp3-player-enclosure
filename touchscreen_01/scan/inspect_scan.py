"""Read-only dimensional inspection of untextured Scaniverse geometry.
Millimetre conversion is from OBJ metadata. Plane leveling and region masks are
analysis choices; they do not turn phone scan geometry into a calibrated drawing.
"""
from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/mytunas-matplotlib')
import numpy as np,trimesh,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent.parent/'revision_04/designs/P04_compact/reference_only/Scaniverse_2026_09_12_145606.obj'
m=trimesh.load(SOURCE,force='mesh',process=False)
v=m.vertices*1000
# Remove background tilt using distant support-surface samples, robust clipping.
bg=(np.hypot(v[:,0],v[:,2])>55)&(np.hypot(v[:,0],v[:,2])<100)
A=np.column_stack((v[:,0],v[:,2],np.ones(len(v))))
for _ in range(5):
    coef=np.linalg.lstsq(A[bg],v[bg,1],rcond=None)[0]
    residual=v[:,1]-A@coef
    bg=bg&(np.abs(residual)<.7)
# World horizontal axes -> portrait panel axes (approximate edge alignment).
a=np.radians(31.5)
x=-np.sin(a)*v[:,0]+np.cos(a)*v[:,2]+2.7
y=np.cos(a)*v[:,0]+np.sin(a)*v[:,2]+5.2
z=v[:,1]-A@coef
p=np.column_stack((x,y,z))
roi=(abs(x)<28)&(y>-48)&(y<29)
fm=roi[m.faces].all(axis=1)
scan=trimesh.Trimesh(p,m.faces[fm],process=False)
scan.remove_unreferenced_vertices()
scan.export(ROOT/'leveled_crop_mm.ply')
fig=plt.figure(figsize=(14,8),facecolor='#f3f6f3')
ax=fig.add_subplot(121)
pts=ax.scatter(x[roi],y[roi],c=z[roi],s=2,cmap='viridis',vmin=0,vmax=8)
ax.set(aspect='equal',xlim=(-28,28),ylim=(-48,29),xlabel='Across panel / mm',ylabel='Along panel / mm',title='Geometry only / leveled and approximately aligned')
ax.grid(alpha=.2);fig.colorbar(pts,ax=ax,shrink=.65,label='Height above fitted support / mm')
ax=fig.add_subplot(122,projection='3d')
verts=scan.vertices
ax.plot_trisurf(verts[:,0],verts[:,1],verts[:,2],triangles=scan.faces,color='#9eaaa2',linewidth=0,antialiased=False,shade=True)
ax.set(xlabel='Across / mm',ylabel='Along / mm',zlabel='Height / mm',zlim=(-1,10))
ax.set_box_aspect((56,77,22));ax.view_init(elev=42,azim=-115)
ax.set_title('Rear relief + ribbon region / untextured mesh')
fig.suptitle('T800 U2 display scan — support surface retained for context',fontsize=16)
fig.tight_layout(rect=(0,0,1,.93));fig.savefig(ROOT/'inspection.png',dpi=180)
report={'source':str(SOURCE.relative_to(ROOT.parent.parent)),'source_units':'meter (explicit OBJ header)','scale_to_mm':1000,'vertices':len(m.vertices),'faces':len(m.faces),'raw_bounds_mm':(m.bounds*1000).tolist(),'missing_referenced_material':'Scaniverse_2026_09_12_145606.mtl','material_found':SOURCE.with_suffix('.mtl').exists(),'support_plane_y_ax_bz_c':coef.tolist(),'support_residual_95_percent_mm':np.percentile(abs(z[bg]),95).item(),'horizontal_alignment_degrees':31.5,'alignment_translation_mm':[2.7,5.2],'scope':'Uncalibrated surface inspection. Includes support surface and scan artifacts. No hidden front-face thickness or connector pitch measurement.'}
# Threshold sensitivity illustrates why a single mesh bounding box is not a part measurement.
report['body_threshold_sensitivity']=[]
for threshold in [.7,1.2,1.8,2.4,3.0]:
    region=(abs(x)<24)&(y>-23)&(y<25)&(z>threshold)&(z<6)
    q=p[region]
    bounds=np.percentile(q,[1,99],axis=0)
    report['body_threshold_sensitivity'].append({'height_threshold_mm':threshold,'points':len(q),'percentile_bounds_mm':bounds.tolist(),'percentile_extents_mm':(bounds[1]-bounds[0]).tolist()})
(ROOT/'scan_report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
