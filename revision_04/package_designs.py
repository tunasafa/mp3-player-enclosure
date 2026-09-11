"""Package P04 deliverables, with file hashes and ZIP integrity checks."""
from pathlib import Path
import hashlib
import json
import zipfile
import trimesh

ROOT = Path(__file__).resolve().parent

def package(target=None):
    report = json.loads((ROOT/'validation.json').read_text())
    for name,digest in report['input_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError(f'Rebuild CAD after changing {name}.')
    if not all(report['minimum_clearance_checks'].values()):
        raise RuntimeError('Minimum clearance checks failed.')
    viewer = json.loads((ROOT/'viewer_validation.json').read_text())
    if viewer['status'] != 'passed' or viewer['preview_sha256'] != hashlib.sha256((ROOT/'preview.html').read_bytes()).hexdigest():
        raise RuntimeError('Verify the current preview before packaging.')
    if report['envelope_collisions'] or report['routing_reserve_collisions']:
        raise RuntimeError('Resolve the recorded CAD collisions before packaging.')
    for entry in report['stls']:
        mesh = trimesh.load_mesh(ROOT/entry['file'], process=True)
        if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and mesh.body_count == 1):
            raise RuntimeError(f'Invalid current STL: {entry["file"]}')
        if not entry['cad_valid'] or entry['solid_count_cad'] != 1:
            raise RuntimeError('CAD validation failed.')
    names = ['BOM.csv','vendor/6309.step','vendor/README.md','vendor/LICENSE-Adafruit-CAD.txt','README.md','HARDWARE_NOTES.md','requirements.json',
             'parameters.json','requirements.txt','build.py',
             'make_viewer.py','make_components.py','make_branding.py','viewer.html','viewer.js','package.json','package-lock.json',
             'vendor/viewer.bundle.js','vendor/LICENSE-viewer.txt','vendor/XIAO-ESP32S3 v2.step',
             'make_drawings.py','make_layout.py','verify_viewer.mjs','package_designs.py',
             'validation.json','viewer_validation.json','preview.html','design_overview.png','design_overview.pdf',
             'internal_layout.png']
    files = [ROOT/name for name in names]
    files += sorted(p for p in (ROOT/'assets').rglob('*') if p.is_file() and not p.name.startswith('.'))
    files += sorted(p for p in (ROOT/'designs').rglob('*') if p.is_file() and not p.name.startswith('.'))
    missing = [str(p) for p in files if not p.is_file()]
    if missing:
        raise RuntimeError(f'Missing deliverables: {missing}')
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (ROOT/'manifest.sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    files.append(ROOT/'manifest.sha256.json')
    target = Path(target) if target else ROOT/'mp3-player-enclosure-P04.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            z.write(p,arcname=Path('mp3-player-enclosure-P04')/p.relative_to(ROOT))
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:
            raise RuntimeError('Archive integrity check failed.')
        for name,digest in hashes.items():
            if hashlib.sha256(z.read('mp3-player-enclosure-P04/'+name)).hexdigest()!=digest:
                raise RuntimeError(f'Archive hash mismatch: {name}')
    print(f'Created {target}: {len(files)} files, {target.stat().st_size:,} bytes; meshes, archive CRCs and SHA-256 verified.')
    return target

if __name__=='__main__':
    package()
