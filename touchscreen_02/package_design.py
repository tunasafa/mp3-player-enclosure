"""Package the current reviewed prototype and exact reproducible source dependencies."""
from pathlib import Path
import csv,json,hashlib,zipfile
ROOT=Path(__file__).resolve().parent
v=json.loads((ROOT/'validation.json').read_text());browser=json.loads((ROOT/'viewer_validation.json').read_text());fit=json.loads((ROOT/'fit_regression.json').read_text())
assert v['passed'] and browser['passed'] and fit['passed']
assert v['parameter_sha256']==browser['parameter_sha256']==fit['parameter_sha256']
data=json.loads((ROOT/'model.json').read_text());assert data['report']==v
with (ROOT/'BOM.csv').open('w',newline='') as fp:
 w=csv.writer(fp);w.writerow(['part_id','quantity','description','type','definition','qualification'])
 for part in data['parts']:
  if part['reserve']:continue
  kind=part['kind'];qualification='Manufacturer CAD; sample fit required' if part['id'] in ['audio','xiao'] else 'Nominal prototype; physical qualification required'
  w.writerow([part['id'],1,part['label'],kind,part['source'],qualification])
for n,h in v['source_sha256'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h
for n,h in v['dependency_sha256'].items():assert hashlib.sha256((ROOT.parent/n).read_bytes()).hexdigest()==h
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.suffix not in ['.zip','.pyc'] and '__pycache__' not in p.parts and 'M02_02' not in p.parts and p.name!='manifest.sha256.json')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
mf=ROOT/'manifest.sha256.json';mf.write_text(json.dumps(manifest,indent=2)+'\n')
dependencies=list(v['dependency_sha256'])+['revision_04/vendor/README.md','revision_04/vendor/LICENSE-Adafruit-CAD.txt','revision_04/vendor/LICENSE-viewer.txt','revision_04/requirements.txt','revision_04/package.json','revision_04/package-lock.json','touchscreen_01/preview.html']
archive=ROOT/'Model02_M02-03_MECHANICAL_PROTOTYPE.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,6) as z:
 for p in files+[mf]+[ROOT.parent/n for n in dependencies]:z.write(p,str(p.relative_to(ROOT.parent)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(f'PASS: packaged {len(files)} files and source dependencies; {archive.stat().st_size/1024/1024:.1f} MiB')
