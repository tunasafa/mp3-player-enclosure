import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { createElement, RotateCcw, ZoomIn, ZoomOut } from 'lucide';

const data = JSON.parse(document.getElementById('model-data').textContent);
const parameters = data.parameters;
document.getElementById('dimensions').textContent = [parameters.body.length, parameters.body.width, parameters.body.thickness].join(' x ');
const canvas = document.getElementById('view');
const scene = new THREE.Scene();
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
} catch (error) {
  document.getElementById('error').style.display = 'block';
  throw error;
}
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
const pmrem = new THREE.PMREMGenerator(renderer);
const room = new RoomEnvironment();
const environment = pmrem.fromScene(room, 0.04);
scene.environment = environment.texture;
scene.environmentIntensity = 0.65;
room.dispose();
pmrem.dispose();
scene.add(new THREE.HemisphereLight(0xffffff, 0x87959d, 1.0));
const keyLight = new THREE.DirectionalLight(0xffffff, 2);
keyLight.position.set(-80, 140, 160);
scene.add(keyLight);
const rearLight = new THREE.DirectionalLight(0xe3eeff, 1.3);
rearLight.position.set(70, 50, -140);
scene.add(rearLight);
const camera = new THREE.OrthographicCamera(-100, 100, 100, -100, 0.1, 1500);
camera.position.z = 400;
const orbit = new THREE.Group();
scene.add(orbit);
const assembly = new THREE.Group();
// CAD uses positive Z into the case. The camera initially faces its front.
assembly.scale.z = -1;
assembly.position.z = parameters.body.thickness / 2;
orbit.add(assembly);
const parts = new Map();
const outlines = [];
const groups = { shell: true, components: true };
const hidden = new Set();
let yaw = -0.50, pitch = -0.14, zoom = 1, explode = 0, outline = false;
let view = 'iso', dirty = false;

const material = (color, metalness = 0, roughness = 0.55) => new THREE.MeshStandardMaterial({ color, metalness, roughness });
function mesh(group, geometry, mat, position = [0,0,0], name = '') {
  const item = new THREE.Mesh(geometry, mat); item.position.set(...position);
  item.name = name; group.add(item); return item;
}
function texture(width, height, draw) {
  const c = document.createElement('canvas');
  c.width = width; c.height = height;
  draw(c.getContext('2d'), width, height);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  return t;
}
function surface(group, width, height, position, map, back = false, transparent = true) {
  if (back) { map.repeat.x = -1; map.offset.x = 1; }
  const mat = new THREE.MeshBasicMaterial({ map, transparent, side: back ? THREE.FrontSide : THREE.BackSide, depthWrite: !transparent, toneMapped: false });
  const item = mesh(group, new THREE.PlaneGeometry(width, height), mat, position);
  item.userData.surface = true;
  return item;
}
function label(group, lines, width, height, position, back = true, background = null, color = '#e9eeee') {
  const map = texture(512, 256, (ctx, w, h) => {
    if (background) { ctx.fillStyle = background; ctx.fillRect(0, 0, w, h); }
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    lines.forEach((line, i) => {
      ctx.font = `${lines.length===1 ? 96 : i ? 26 : 36}px Arial`;
      ctx.fillText(line, w / 2, lines.length===1 ? 165 : 56 + i * 48, w - 30);
    });
  });
  return surface(group, width, height, position, map, back);
}
function decode(value) {
  const bytes = Uint8Array.from(atob(value), c => c.charCodeAt(0));
  return new Float32Array(bytes.buffer);
}
function imported(group, positions, mat) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(decode(positions), 3));
  geometry.computeVertexNormals();
  return mesh(group, geometry, mat);
}

for (const spec of data.parts) {
  const group = new THREE.Group(); group.name = spec.id; group.userData = spec;
  parts.set(spec.id, group); assembly.add(group);
  if (spec.batches) for (const batch of spec.batches) imported(group, batch.positions,
    material(batch.color_linear ? new THREE.Color().setRGB(...batch.color_linear, THREE.LinearSRGBColorSpace) : batch.color, ['front_bezel','rear_shell'].includes(spec.id) ? .72 : .22, ['front_bezel','rear_shell'].includes(spec.id) ? .35 : .48));
  else imported(group, spec.positions, material(spec.color, spec.id === 'battery' ? .45 : .06, .52));
  if (spec.engraving_positions) imported(group, spec.engraving_positions, material('#344d49', .1, .7));
}
const d = parameters.display, aw = data.validation.derived.active_area_mm[1], ah = data.validation.derived.active_area_mm[0];
const screen = texture(592,480,(ctx,w,h)=>{
  ctx.fillStyle='#0b2226';ctx.fillRect(0,0,w,h);
  ctx.fillStyle='#85aaa1';ctx.font='17px Arial';ctx.fillText('LOCAL COLLECTION',35,43);
  ctx.fillStyle='#c4dfb8';ctx.fillRect(511,29,34,14);ctx.fillRect(547,33,3,6);
  const gradient=ctx.createLinearGradient(38,85,260,335);gradient.addColorStop(0,'#c9dba0');gradient.addColorStop(.45,'#659e82');gradient.addColorStop(1,'#1f525a');
  ctx.fillStyle=gradient;ctx.beginPath();ctx.roundRect(35,80,232,238,14);ctx.fill();
  ctx.save();ctx.beginPath();ctx.roundRect(35,80,232,238,14);ctx.clip();
  for(let i=0;i<12;i++){ctx.strokeStyle='rgba(237,249,208,.14)';ctx.lineWidth=5;ctx.beginPath();ctx.arc(240,92,25+i*22,0,Math.PI*2);ctx.stroke();}ctx.restore();
  ctx.fillStyle='#d8e8d5';ctx.font='16px Arial';ctx.fillText('NOW PLAYING',300,106);
  ctx.fillStyle='#eff3e7';ctx.font='bold 29px Arial';ctx.fillText('A place of',300,154);ctx.fillText('your own',300,191);
  ctx.font='18px Arial';ctx.fillStyle='#8daf9f';ctx.fillText('mytunas',300,227);
  ctx.fillStyle='#c8e1b8';ctx.beginPath();ctx.arc(412,287,28,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#153931';ctx.fillRect(403,276,5,23);ctx.fillRect(416,276,5,23);
  for(const x of [333,490]){ctx.fillStyle='#bad0bc';ctx.beginPath();ctx.moveTo(x+(x<400?7:-7),277);ctx.lineTo(x+(x<400?-8:8),287);ctx.lineTo(x+(x<400?7:-7),297);ctx.fill();}
  ctx.fillStyle='#31574f';ctx.fillRect(35,359,520,4);ctx.fillStyle='#c5dfad';ctx.fillRect(35,359,185,4);
  ctx.font='16px Arial';ctx.fillStyle='#91afa0';ctx.fillText('1:24',35,389);ctx.fillText('4:08',522,389);
  ctx.fillStyle='#719487';ctx.font='15px Arial';ctx.fillText('LIBRARY',60,440);ctx.fillText('PLAYING',255,440);ctx.fillText('SETTINGS',458,440);
});
// Rounded active estimate respects the large corner radii in the actual photo.
// One display surface only; all four physical layers come from CAD.
const uiShape=new THREE.Shape(),rw=aw,rh=ah,rr=5.3;
uiShape.moveTo(-rw/2+rr,-rh/2);uiShape.lineTo(rw/2-rr,-rh/2);uiShape.quadraticCurveTo(rw/2,-rh/2,rw/2,-rh/2+rr);uiShape.lineTo(rw/2,rh/2-rr);uiShape.quadraticCurveTo(rw/2,rh/2,rw/2-rr,rh/2);uiShape.lineTo(-rw/2+rr,rh/2);uiShape.quadraticCurveTo(-rw/2,rh/2,-rw/2,rh/2-rr);uiShape.lineTo(-rw/2,-rh/2+rr);uiShape.quadraticCurveTo(-rw/2,-rh/2,-rw/2+rr,-rh/2);
const uiGeometry=new THREE.ShapeGeometry(uiShape,20),uv=uiGeometry.attributes.uv,pos=uiGeometry.attributes.position;
for(let i=0;i<uv.count;i++)uv.setXY(i,(pos.getX(i)+rw/2)/rw,(pos.getY(i)+rh/2)/rh);
const lcd=mesh(parts.get('touch_glass'),uiGeometry,new THREE.MeshBasicMaterial({map:screen,side:THREE.BackSide,toneMapped:false}),[...d.center,d.glass_z-.012],'touch-ui');lcd.userData.surface=true;
const b=parameters.battery;
label(parts.get('battery'),['503040 / 1S LiPo','600 mAh nominal','40 × 30 × 5 mm'],27,13,[...b.center,b.z+b.size[2]+.012],true,'#e0e5d8','#304a45');
label(parts.get('lcd'),['JL-M201B002-01','LCD + BACKLIGHT'],22,8,[...d.center,d.lcd_z+d.lcd_size[2]+.012],true,null,'#465355');
label(parts.get('front_bezel'),['mytunas'],23,7,[0,-23,-.012],false,null,'#405d54');
for (const group of parts.values()) {
  group.traverse(item => {
    if (!item.isMesh || item.userData.surface || item.material.transparent) return;
    const lines = new THREE.LineSegments(new THREE.EdgesGeometry(item.geometry, 35), new THREE.LineBasicMaterial({ color: '#172229', transparent: true, opacity: 0.3 }));
    lines.visible = false; lines.userData.outline = true;
    item.add(lines); outlines.push(lines);
  });
}

function visibleParts() { return [...parts.values()].filter(p => p.visible); }
function updateVisibility() {
  for (const [id, group] of parts) {
    group.visible = groups[group.userData.group] && !hidden.has(id) && !(view === 'inside' && ['rear_shell','rear_gasket','rear_liner','dac_retention','case_screws'].includes(id));
    group.position.z = explode * 0.43 * group.userData.explode;
  }
  for (const lines of outlines) lines.visible = outline;
}
function axes() {
  const ctx = document.getElementById('axis').getContext('2d');
  ctx.clearRect(0, 0, 130, 130); ctx.font = '15px monospace'; ctx.lineWidth = 2;
  for (const [v, text, color] of [[[1, 0, 0], 'X', '#b06a59'], [[0, 1, 0], 'Y', '#478875'], [[0, 0, -1], 'Z', '#4f82ab']]) {
    const p = new THREE.Vector3(...v).applyEuler(orbit.rotation);
    ctx.strokeStyle = color; ctx.fillStyle = color; ctx.beginPath(); ctx.moveTo(57, 69); ctx.lineTo(57 + p.x * 32, 69 - p.y * 32); ctx.stroke(); ctx.fillText(text, 52 + p.x * 47, 74 - p.y * 47);
  }
}
function render() {
  dirty = false;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  const aspect = w / h;
  const compact = w < 480;
  orbit.rotation.set(pitch,yaw,0,'XYZ');orbit.position.y=0;updateVisibility();orbit.updateMatrixWorld(true);
  const fit=new THREE.Box3();for(const p of visibleParts())fit.union(new THREE.Box3().setFromObject(p));
  const size=fit.getSize(new THREE.Vector3()),center=fit.getCenter(new THREE.Vector3());
  // Reserve real stage space for controls; fit the visible exploded bounds.
  const span=Math.max(size.y*(compact?1.75:1.48),size.x/aspect*1.28,80)/zoom;
  camera.left=-span*aspect/2;camera.right=span*aspect/2;camera.top=span/2;camera.bottom=-span/2;
  camera.position.set(center.x,center.y+(compact?3:0),400);camera.updateProjectionMatrix();
  renderer.render(scene, camera); axes();
  document.getElementById('meshcount').textContent = `${visibleParts().length} PARTS / ${renderer.info.render.triangles.toLocaleString()} TRIANGLES`;
}
function invalidate() { if (!dirty) { dirty = true; requestAnimationFrame(render); } }
function legend() {
  const el = document.getElementById('legend'); el.replaceChildren();
  for (const [id, group] of parts) {
    const row = document.createElement('button');
    row.className = `legend-row${group.visible ? '' : ' off'}`;
    row.dataset.part = id; row.title = group.userData.source;
    row.setAttribute('aria-pressed', String(group.visible));
    const swatch = document.createElement('span'); swatch.className = 'swatch'; swatch.style.background = group.userData.color;
    row.append(swatch, document.createTextNode(group.userData.label));
    row.onclick = () => {
      // Parts selected while inside remain inspectable without restoring both shells.
      if (view === 'inside' && id === 'rear_shell') {
        view = 'custom';
        for (const [otherId, other] of parts) if (!other.visible) hidden.add(otherId);
      }
      if (!groups[group.userData.group]) {
        for (const [otherId, other] of parts) if (other.userData.group === group.userData.group) hidden.add(otherId);
        groups[group.userData.group] = true;
      }
      group.visible ? hidden.add(id) : hidden.delete(id);
      updateControls();
    };
    el.append(row);
  }
}
function updateControls() {
  updateVisibility(); legend();
  document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
  document.querySelectorAll('[data-group]').forEach(c => {
    const members = [...parts.values()].filter(p => p.userData.group === c.dataset.group);
    const visible = members.filter(p => p.visible).length;
    c.checked = visible === members.length;
    c.indeterminate = visible > 0 && visible < members.length;
  });
  document.getElementById('viewname').textContent = view === 'inside' ? 'Inside / rear shell removed' : explode ? 'Exploded assembly' : 'Touch / 8.3 mm metal prototype';
  invalidate();
}
document.querySelectorAll('[data-view]').forEach(b => b.onclick = () => {
  view = b.dataset.view;
  if (view === 'front') { yaw = 0; pitch = 0; }
  else if (view === 'back') { yaw = Math.PI; pitch = 0; }
  else if (view === 'inside') { yaw = Math.PI + 0.24; pitch = -0.16; groups.components = true; for (const [id, p] of parts) if (p.userData.group === 'components') hidden.delete(id); }
  else if (view === 'ports') {yaw=-.55;pitch=-1.02;}
  else { yaw = -0.5; pitch = -0.14; }
  updateControls();
});
document.getElementById('explode').oninput = e => {
  const old = explode; explode = Number(e.target.value);
  document.getElementById('explode-out').textContent = `${explode}%`;
  if (!old && explode > 0 && Math.abs(Math.sin(yaw)) < 0.2) yaw -= 0.65;
  updateControls();
};
document.querySelectorAll('[data-group]').forEach(c => c.onchange = () => {
  if (c.dataset.group === 'shell' && view === 'inside') view = 'custom';
  groups[c.dataset.group] = c.checked;
  if (c.checked) for (const [id, p] of parts) if (p.userData.group === c.dataset.group) hidden.delete(id);
  updateControls();
});
document.getElementById('outlines').onchange = e => { outline = e.target.checked; invalidate(); };
document.getElementById('reset').onclick = () => {
  yaw = -0.5; pitch = -0.14; zoom = 1; explode = 0; outline = false; view = 'iso';
  hidden.clear(); groups.shell = true; groups.components = true;
  document.getElementById('explode').value = 0; document.getElementById('explode-out').textContent = '0%';
  document.getElementById('outlines').checked = false; updateControls();
};
function setZoom(value) { zoom = THREE.MathUtils.clamp(value, 0.5, 3); invalidate(); }
document.getElementById('zoom-in').onclick = () => setZoom(zoom * 1.15);
document.getElementById('zoom-out').onclick = () => setZoom(zoom / 1.15);
for (const [id, icon] of [['reset', RotateCcw], ['zoom-in', ZoomIn], ['zoom-out', ZoomOut]]) document.getElementById(id).append(createElement(icon));
const pointers = new Map();
let pinchDistance = null;
canvas.onpointerdown = e => {
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY }); canvas.setPointerCapture(e.pointerId); canvas.classList.add('dragging');
};
canvas.onpointermove = e => {
  const previous = pointers.get(e.pointerId); if (!previous) return;
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (pointers.size === 2) {
    const [a, b] = [...pointers.values()], distance = Math.hypot(a.x - b.x, a.y - b.y);
    if (pinchDistance) setZoom(zoom * distance / pinchDistance);
    pinchDistance = distance;
  } else {
    yaw += (e.clientX - previous.x) * 0.009;
    pitch = THREE.MathUtils.clamp(pitch + (e.clientY - previous.y) * 0.009, -Math.PI / 2, Math.PI / 2);
    invalidate();
  }
};
function endPointer(e) { pointers.delete(e.pointerId); pinchDistance = null; if (!pointers.size) canvas.classList.remove('dragging'); }
canvas.onpointerup = endPointer; canvas.onpointercancel = endPointer; canvas.onlostpointercapture = endPointer;
canvas.addEventListener('wheel', e => { e.preventDefault(); setZoom(zoom * Math.exp(-e.deltaY * 0.001)); }, { passive: false });
canvas.onkeydown = e => {
  if (e.key === 'ArrowLeft') yaw -= 0.12;
  else if (e.key === 'ArrowRight') yaw += 0.12;
  else if (e.key === 'ArrowUp') pitch = Math.max(-Math.PI / 2, pitch - 0.12);
  else if (e.key === 'ArrowDown') pitch = Math.min(Math.PI / 2, pitch + 0.12);
  else if (e.key === '+' || e.key === '=') setZoom(zoom * 1.1);
  else if (e.key === '-') setZoom(zoom / 1.1);
  else if (e.key === 'Home') document.getElementById('reset').click();
  else return;
  e.preventDefault(); invalidate();
};
canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); document.getElementById('error').style.display = 'block'; });
canvas.addEventListener('webglcontextrestored', () => { document.getElementById('error').style.display = 'none'; invalidate(); });
new ResizeObserver(invalidate).observe(canvas);
updateControls();
window.T01 = {
 getState:()=>({variant:'T03_metal',view,explode,zoom,visible:visibleParts().length,hidden:[...hidden]}),
 getInspection:()=>({parameters,ids:[...parts.keys()],screen:{width:aw,height:ah,parent:lcd.parent.name},validated:data.validation.passed,validation:data.validation,
 geometry:[...parts].map(([id,group])=>{
  const physical=group.children.filter(m=>m.isMesh&&!m.userData.surface);const bound=new THREE.Box3();
  let triangles=0;for(const m of physical){m.geometry.computeBoundingBox();bound.union(m.geometry.boundingBox);triangles+=m.geometry.attributes.position.count/3;}
  return {id,bounds:[bound.min.toArray(),bound.max.toArray()],expected:group.userData.bounds_mm,physicalMeshes:physical.length,expectedMeshes:group.userData.batches.length,triangles,surfaces:group.children.filter(m=>m.userData.surface).map(m=>m.name)};
 })}),render:invalidate
};
