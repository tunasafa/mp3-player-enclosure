"""Independently inspect delivered meshes and the unsliced 3MF build plate."""
from pathlib import Path
import json, zipfile
from xml.etree import ElementTree as ET
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parent
expected={'front_tray','rear_lid','carrier','xiao_gate','coupon_receiver','coupon_lid'}
checks={}
for name in sorted(expected):
    m=trimesh.load_mesh(ROOT/'parts'/f'{name}.stl')
    assert m.is_watertight and m.is_winding_consistent and m.body_count==1,name
    assert np.isfinite(m.vertices).all() and m.volume>0,name
    assert np.max(np.abs(m.bounds[0]))<.0001,(name,m.bounds)
    checks[name]={'size_mm':m.extents.tolist(),'volume_mm3':float(m.volume),'watertight':True}

ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(ROOT/'M02-P01_MK3S_PLA_UNSLICED.3mf') as z:
    assert z.testzip() is None
    xml=ET.fromstring(z.read('3D/3dmodel.model'))
assert xml.attrib['unit']=='millimeter'
objects={o.attrib['id']:o for o in xml.findall('m:resources/m:object',ns)}
assert {o.attrib['name'] for o in objects.values()}==expected
rectangles=[]
for item in xml.findall('m:build/m:item',ns):
    o=objects[item.attrib['objectid']];name=o.attrib['name']
    vs=np.array([[float(v.attrib[k]) for k in ['x','y','z']] for v in o.findall('m:mesh/m:vertices/m:vertex',ns)])
    fs=np.array([[int(f.attrib[k]) for k in ['v1','v2','v3']] for f in o.findall('m:mesh/m:triangles/m:triangle',ns)])
    m=trimesh.Trimesh(vs,fs,process=True)
    assert m.is_watertight and m.body_count==1,name
    assert np.allclose(m.extents,checks[name]['size_mm'],atol=.0001),name
    tr=list(map(float,item.attrib['transform'].split()))
    assert tr[:9]==[1,0,0,0,1,0,0,0,1]
    lo=m.bounds[0]+tr[9:];hi=m.bounds[1]+tr[9:]
    assert lo[0]>=0 and lo[1]>=0 and hi[0]<=250 and hi[1]<=210,name
    for other,a,b in rectangles:
        assert hi[0]<=a[0] or lo[0]>=b[0] or hi[1]<=a[1] or lo[1]>=b[1],(name,other)
    rectangles.append((name,lo,hi))
    checks[name]['bed_min_mm']=lo.tolist();checks[name]['bed_max_mm']=hi.tolist()
result={'passed':True,'scope':'Delivered STL/3MF manifold meshes, size agreement, bed orientation and non-overlapping plate; no toolpath slicing.',
        'slicer_verified':False,'parts':checks}
(ROOT/'print_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: six manifold print meshes, identical STL/3MF sizes, Z0 orientation, non-overlapping MK3S+ bed layout.')
