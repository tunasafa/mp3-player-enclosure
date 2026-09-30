"""Package a reviewed print fixture, keeping electronics out of print files."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent
report=json.loads((ROOT/'validation.json').read_text())
viewer=json.loads((ROOT/'viewer_validation.json').read_text())
prints=json.loads((ROOT/'print_validation.json').read_text())
assert report['passed'] and viewer['passed'] and prints['passed']
assert report['source_sha256']==viewer['source_sha256']
for name,h in report['source_sha256'].items():
    assert hashlib.sha256((ROOT.parents[1]/name).read_bytes()).hexdigest()==h
names=['README.md','validation.json','viewer_validation.json','print_validation.json','M02-P01_MK3S_PLA_UNSLICED.3mf',
       'assembly_REFERENCE_ONLY.step','preview.html','preview_iso.png','preview_inside.png',
       'preview_supports.png','preview_exploded.png','preview_rear.png','preview_latch.png','geometry_pla.py','build.py',
       'viewer.js','viewer.html','verify_viewer.mjs','verify_prints.py','package.py']
files=[ROOT/n for n in names]+sorted((ROOT/'parts').glob('*'))
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(ROOT/'manifest.sha256.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(ROOT/'M02-P01_PLA_FIT_PROTOTYPE.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[ROOT/'manifest.sha256.json']:
        z.write(p,'M02-P01/'+str(p.relative_to(ROOT)))
    # Source build depends on the repository; include evidence/attribution, not
    # a misleading claim that this lightweight print download is standalone code.
    for p in [ROOT.parent/'COMPONENT_DIMENSIONS.md',ROOT.parent/'RELEASE_CHECKLIST.md',
              ROOT.parents[1]/'revision_04/vendor/LICENSE-Adafruit-CAD.txt',
              ROOT.parents[1]/'revision_04/vendor/LICENSE-viewer.txt']:
        z.write(p,'M02-P01/reference/'+p.name)
    z.write(ROOT.parents[1]/'revision_04/vendor/README.md','M02-P01/reference/COMPONENT_CAD_PROVENANCE.md')
with zipfile.ZipFile(ROOT/'M02-P01_PLA_FIT_PROTOTYPE.zip') as z:assert z.testzip() is None
print('PASS: packaged four assembly STLs, two coupon STLs, oriented 3MF, assembly reference, preview and instructions.')
