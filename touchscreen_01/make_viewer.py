"""Package the exact validated assembly meshes; no alternative display geometry."""
from pathlib import Path
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parent

def main():
 data=json.loads((ROOT/'model_data.json').read_text());v=json.loads((ROOT/'validation.json').read_text())
 if not v['passed'] or data['validation']!=v:raise RuntimeError('Rebuild and validate CAD first')
 for name,digest in {'parameters.json':v['parameter_sha256'],**v['source_sha256']}.items():
  if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:raise RuntimeError(f'Stale validated geometry: {name}')
 subprocess.run([str(ROOT.parent/'revision_04/node_modules/.bin/esbuild'),str(ROOT/'viewer.js'),'--bundle','--minify','--format=iife',f'--outfile={ROOT}/vendor/viewer.bundle.js'],env=os.environ|{'NODE_PATH':str(ROOT.parent/'revision_04/node_modules')},check=True)
 html=(ROOT/'viewer.html').read_text().replace('__MODEL_DATA__',json.dumps(data,separators=(',',':')))
 html=html.replace('__VIEWER_SCRIPT__',(ROOT/'vendor/viewer.bundle.js').read_text().replace('</script','<\\/script'))
 html=html.replace('__VIEWER_LICENSES__',(ROOT.parent/'revision_04/vendor/LICENSE-viewer.txt').read_text())
 (ROOT/'historical_preview.html').write_text(html)
 print('Wrote historical offline T02 viewer with validated shared CAD geometry.')
if __name__=='__main__':main()
