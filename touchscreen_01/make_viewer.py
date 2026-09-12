"""Embed validated CAD meshes in the offline T01 viewer. No external assets."""
from pathlib import Path
import base64
import json
import subprocess
import sys
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'revision_04'))
from make_components import vendor_meshes

def packed(a): return base64.b64encode(np.asarray(a,dtype='<f4').tobytes()).decode('ascii')

def main():
    p=json.loads((ROOT/'parameters.json').read_text())
    v=json.loads((ROOT/'validation.json').read_text())
    if not v['passed']: raise RuntimeError('Build and validate CAD first')
    subprocess.run([str(ROOT.parent/'revision_04/node_modules/.bin/esbuild'),str(ROOT/'viewer.js'),'--bundle','--minify','--format=iife',f'--outfile={ROOT}/vendor/viewer.bundle.js'],env=__import__('os').environ|{'NODE_PATH':str(ROOT.parent/'revision_04/node_modules')},check=True)
    specs=[('front_bezel','Front bezel','shell','#ccdbd6',-1.1),('rear_shell','Rear shell / engraved','shell','#8eaaa2',1.2),('touch_glass','Cover glass / 0.25 mm','components','#101b20',-.85),('touch_sensor','Touch sensor / 0.7 mm','components','#344c45',-.75),('touch_lcd_tape','Touch–LCD tape / 0.2 mm','components','#c5a368',-.70),('lcd','LCD + backlight / 2.15 mm','components','#6a7980',-.65),('battery_tray','Removable battery tray','shell','#a9bfb5',.1),('battery','3.4 mm battery / unselected','components','#c1c8c5',.35)]
    specs += [(e['id'],e['label'],'components','#b88c5b' if e['id']=='audio' else '#397466',.65) for e in p['electronics']]
    parts=[]
    for id,label,group,color,explode in specs:
        spec=dict(id=id,label=label,group=group,color=color,explode=explode,source='Nominal CAD allowance; see hardware audit' if group=='components' else 'T01 shell CAD')
        if id=='xiao':
            e=next(e for e in p['electronics'] if e['id']=='xiao')
            def transform(a): return np.column_stack((-a[:,2]-6.1114+e['center'][0],-a[:,0]+e['center'][1]+1.80475,a[:,1]+.25+e['z']))
            spec['batches']=vendor_meshes('xiao',transform)
            spec['source']='Seeed manufacturer STEP / unscaled'
        elif id=='audio':
            e=next(e for e in p['electronics'] if e['id']=='audio')
            def transform(a):
                return np.column_stack((a[:,0]-16.85+e['center'][0],a[:,1]-12.7+e['center'][1],a[:,2]+e['z']))
            spec['batches']=vendor_meshes('dac',transform)
            spec['source']='Adafruit TLV320DAC3100 #6309 manufacturer STEP / unscaled'
        else:
            mesh=trimesh.load_mesh(ROOT/'designs/T01_concept/reference_only'/f'{id}.stl',process=True)
            spec['positions']=packed(mesh.triangles.reshape(-1,3))
            if id=='rear_shell':
                mask=np.all(np.isclose(mesh.triangles[:,:,2],p['body']['thickness']-p['branding']['depth'],atol=1e-4),axis=1)&(mesh.face_normals[:,2]>.99)
                spec['positions']=packed(mesh.triangles[~mask].reshape(-1,3))
                spec['engraving_positions']=packed(mesh.triangles[mask].reshape(-1,3))
        parts.append(spec)
    data={'parameters':p,'parts':parts,'validation':v}
    html=(ROOT/'viewer.html').read_text().replace('__MODEL_DATA__',json.dumps(data,separators=(',',':')))
    html=html.replace('__VIEWER_SCRIPT__',(ROOT/'vendor/viewer.bundle.js').read_text().replace('</script','<\\/script'))
    html=html.replace('__VIEWER_LICENSES__',(ROOT.parent/'revision_04/vendor/LICENSE-viewer.txt').read_text())
    (ROOT/'preview.html').write_text(html)
    print('Wrote offline touchscreen_01/preview.html')

if __name__=='__main__': main()
