from pathlib import Path
import os,base64,json,subprocess
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
m=trimesh.load_mesh(ROOT/'leveled_crop_mm.ply',process=False)
def pack(a,dtype):return base64.b64encode(np.asarray(a,dtype=dtype).tobytes()).decode('ascii')
data={'vertices':pack(m.vertices,'<f4'),'faces':pack(m.faces,'<u4'),'triangle_count':len(m.faces)}
subprocess.run([str(REPO/'revision_04/node_modules/.bin/esbuild'),str(ROOT/'viewer.js'),'--bundle','--minify','--format=iife',f'--outfile={ROOT}/viewer.bundle.js'],env=os.environ|{'NODE_PATH':str(REPO/'revision_04/node_modules')},check=True)
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>mytunas / display scan</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f1f5f1;color:#29443a;font:15px Arial}header,footer{padding:20px 5%;line-height:1.6}h1{font-size:24px;margin:0 0 6px}p{margin:5px 0}canvas{display:block;width:100%;height:65vh;min-height:340px}nav{display:flex;gap:12px;flex-wrap:wrap;padding:12px 5%;align-items:center}button{padding:8px 14px;background:#e4eee6;border:1px solid #9eb4a5;border-radius:4px;color:inherit;cursor:pointer}a{color:#346b52}small{color:#61796b}</style>
<header><h1>Display scan / T800 U2</h1><p>Untextured rear geometry and ribbon region · millimetres · grid spacing 5 mm</p><small>Scale from OBJ metadata. Support surface retained. Approximate alignment; scan is not a calibrated part drawing.</small></header>
<canvas aria-label="Interactive display scan; drag to orbit and scroll to zoom"></canvas>
<nav><button data-view="rear">Rear</button><button data-view="side">Side</button><button data-view="iso">3D</button><label><input id="wire" type="checkbox"> Mesh edges</label><label><input id="grid" type="checkbox" checked> Grid</label></nav>
<footer><a href="../preview.html">Enclosure model</a> · <a href="README.md">Scan findings</a><p>Matching .mtl and textures were not available. Thin flex layers and hidden front thickness remain unresolved.</p></footer>
<script id="data" type="application/json">__DATA__</script><script>__SCRIPT__</script></html>'''
html=html.replace('__DATA__',json.dumps(data,separators=(',',':'))).replace('__SCRIPT__',(ROOT/'viewer.bundle.js').read_text().replace('</script','<\\/script'))
license=(REPO/'revision_04/vendor/LICENSE-viewer.txt').read_text()
(ROOT/'preview.html').write_text(html.replace('<html lang="en">','<html lang="en"><!--'+license+'-->'))
print('Wrote interactive scan viewer')
