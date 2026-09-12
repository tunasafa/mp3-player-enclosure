import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
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
const mats = {
  pcb: material('#17664e', 0.05, 0.6), blue: material('#175d9a', 0.06, 0.6),
  black: material('#111820', 0, 0.7), dark: material('#30363b', 0.1, 0.4),
  silver: material('#b8c2cc', 0.86, 0.28), solder: material('#b6bec1', 0.8, 0.37),
  gold: material('#d4aa45', 0.82, 0.27), copper: material('#ae782d', 0.7, 0.42),
  ceramic: material('#a99573', 0, 0.6), white: material('#e9e8e3', 0, 0.4),
  wheel: material('#d3d7d9', 0.03, 0.4), flex: material('#ba6d18', 0.2, 0.42),
  tape: material('#eab128', 0.15, 0.3), red: material('#be2534', 0, 0.58),
};
function mesh(group, geometry, mat, position = [0, 0, 0], name = '') {
  const item = new THREE.Mesh(geometry, mat);
  item.position.set(...position);
  item.name = name;
  group.add(item);
  return item;
}
function box(group, size, position, mat, radius = 0) {
  const geometry = radius ? new RoundedBoxGeometry(...size, 2, Math.min(radius, ...size.map(n => n / 2 - 0.001))) : new THREE.BoxGeometry(...size);
  return mesh(group, geometry, mat, position);
}
function cylinder(group, radius, height, position, mat, segments = 48) {
  const geometry = new THREE.CylinderGeometry(radius, radius, height, segments);
  geometry.rotateX(Math.PI / 2);
  return mesh(group, geometry, mat, position);
}
function ring(group, outer, inner, position, mat) {
  return mesh(group, new THREE.RingGeometry(inner, outer, 32), mat, position);
}
function path(group, points, radius, mat) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)), false, 'centripetal');
  return mesh(group, new THREE.TubeGeometry(curve, 32, radius, 7, false), mat);
}
function ribbon(group, points, width) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  const vertices = [], indices = [];
  for (let i = 0; i <= 32; i++) {
    const p = curve.getPoint(i / 32);
    vertices.push(p.x - width / 2, p.y, p.z, p.x + width / 2, p.y, p.z);
    if (i < 32) { const n = i * 2; indices.push(n, n + 1, n + 2, n + 1, n + 3, n + 2); }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  const mat = mats.flex.clone(); mat.side = THREE.DoubleSide;
  mesh(group, geometry, mat);
  for (let i = 0; i < Math.min(8, Math.max(2, Math.round(width))); i++) {
    path(group, curve.getPoints(16).map(p => [p.x + (i - 3.5) * width / 8, p.y, p.z + .045]), .035, mats.copper);
  }
}
function board(group,width,height,thickness,position,mat,holes=[]) {
  box(group,[width,height,thickness],position,mat,.7);
  for (const [hx,hy,r] of holes) { ring(group,r+.45,r,[position[0]+hx,position[1]+hy,position[2]+thickness+.02],mats.gold); }
}
function passive(group,x,y,z,width=1.4,length=.75,mat=mats.ceramic) {
  box(group,[width,length,.45],[x,y,z+.225],mat,.08);
  for (const dx of [-width*.4,width*.4]) box(group,[width*.22,length+.05,.48],[x+dx,y,z+.24],mats.solder);
}
function chip(group,x,y,z,width,height) {
  box(group,[width,height,.65],[x,y,z+.325],mats.black,.12);
  for (let i=0;i<5;i++) for (const side of [-1,1]) box(group,[.7,.25,.18],[x+side*(width/2+.2),y+(i-2)*height/5,z+.1],mats.solder);
  cylinder(group,.16,.02,[x-width/2+.45,y+height/2-.45,z+.66],mats.dark,12);
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
      ctx.font = `${i ? 26 : 36}px Arial`;
      ctx.fillText(line, w / 2, 56 + i * 48, w - 30);
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
    material(new THREE.Color().setRGB(...batch.color, THREE.LinearSRGBColorSpace), .35, .5));
  else imported(group, spec.positions, material(spec.color, spec.id === 'battery' ? .45 : .06, .52));
  if (spec.engraving_positions) imported(group, spec.engraving_positions, material('#344d49', .1, .7));
}
const d = parameters.display, aw = data.validation.derived.active_area_mm[0], ah = data.validation.derived.active_area_mm[1];
const screen = texture(480, 592, (ctx,w,h) => {
  ctx.fillStyle='#0c2021'; ctx.fillRect(0,0,w,h);
  ctx.fillStyle='#9cbbb1'; ctx.font='20px Arial'; ctx.fillText('MY LIBRARY',30,36);
  ctx.fillStyle='#b3e6c9'; ctx.fillRect(394,21,43,17);ctx.fillRect(440,26,4,7);
  const grad=ctx.createLinearGradient(80,70,400,350); grad.addColorStop(0,'#d3e7b8');grad.addColorStop(.5,'#549c88');grad.addColorStop(1,'#153f48');
  ctx.fillStyle=grad;ctx.beginPath();ctx.roundRect(84,65,312,266,14);ctx.fill();
  ctx.save();ctx.beginPath();ctx.roundRect(84,65,312,266,14);ctx.clip();
  for(let i=0;i<13;i++){ctx.strokeStyle=`rgba(235,247,210,${.08+i*.012})`;ctx.lineWidth=8;ctx.beginPath();ctx.arc(390,95,45+i*22,0,Math.PI*2);ctx.stroke();}ctx.restore();
  ctx.fillStyle='#eff5e9';ctx.font='bold 27px Arial';ctx.fillText('A place of your own',30,377);
  ctx.font='21px Arial';ctx.fillStyle='#93b4aa';ctx.fillText('mytunas / Local collection',30,408);
  ctx.fillStyle='#31544b';ctx.fillRect(30,439,420,4);ctx.fillStyle='#bfdfab';ctx.fillRect(30,439,146,4);
  ctx.font='17px Arial';ctx.fillStyle='#93b4aa';ctx.fillText('1:24',30,468);ctx.fillText('4:08',411,468);
  ctx.fillStyle='#cfe8ba';ctx.beginPath();ctx.arc(240,519,34,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#10302b';ctx.fillRect(229,505,7,28);ctx.fillRect(245,505,7,28);
  for(const x of [130,350]){ctx.fillStyle='#c0d3c5';ctx.beginPath();if(x<240){ctx.moveTo(x+9,507);ctx.lineTo(x-9,519);ctx.lineTo(x+9,531);}else{ctx.moveTo(x-9,507);ctx.lineTo(x+9,519);ctx.lineTo(x-9,531);}ctx.closePath();ctx.fill();ctx.fillRect(x<240?x-14:x+11,507,3,24);}
  ctx.fillStyle='#6b9184';ctx.fillRect(185,575,110,4);
});
const lcd=surface(parts.get('touch_glass'),aw,ah,[...d.center,d.glass_z-.012],screen,false,false);
lcd.name='touch-ui';
for(const id of ['battery','audio','interface_pcb','microsd','display_zif','touch_zif','control']){
  const e=id==='battery'?parameters.battery:parameters.electronics.find(e=>e.id===id);
  const text=id==='battery'?['PROTECTED LiPo','34 × 30 × 3.4','CAPACITY TBD']:id==='audio'?['AUDIO + JACK','18 × 22 × 5.2','DESIGN ALLOWANCE']:id==='interface_pcb'?['CUSTOM INTERFACE']:id==='microsd'?['microSD']:id==='control'?['I/O + POWER']:id==='display_zif'?['DISPLAY / 15P']:['TOUCH / 6P'];
  label(parts.get(id),text,Math.min(e.size[0]-.6,28),Math.min(e.size[1]-.4,15),[...e.center,e.z+e.size[2]+.014],true,null,id==='battery'?'#273c3b':'#eff4dc');
}
const hint=label(parts.get('front_bezel'),['mytunas'],21,6,[0,-28,-.015],false,null,'#446057');

// Detailed visual assembly. These meshes sit inside the validated envelopes and
// are presentation geometry; the parametric CAD remains the fit authority.
function detailedDisplay(group) {
  const [x,y]=d.center,z=d.glass_z;
  box(group,[d.glass_size[0],d.glass_size[1],d.glass_size[2]],[x,y,z+d.glass_size[2]/2],mats.silver,2.5);
  box(group,[d.glass_size[0]-.8,d.glass_size[1]-.8,.08],[x,y,z+d.glass_size[2]+.05],mats.black,2.3);
  box(group,[d.glass_size[0]-1.4,d.glass_size[1]-1.4,d.sensor_thickness],[x,y,z+d.glass_size[2]+d.sensor_thickness/2+.07],mats.wheel,2.3);
  const ui=surface(group,aw,ah,[x,y,z+d.glass_size[2]+d.sensor_thickness+.08],screen,false,false);ui.name='touch-ui';
  const lcdz=d.lcd_z; box(group,[d.lcd_size[0],d.lcd_size[1],d.lcd_size[2]],[x,y,lcdz+d.lcd_size[2]/2],mats.silver,1.6);
  box(group,[d.lcd_size[0]-1.4,d.lcd_size[1]-1.4,.3],[x,y,lcdz+d.lcd_size[2]+.05],mats.black,1.2);
  ribbon(group,[[x-5,y-d.glass_size[1]/2,z+1.2],[x-5,y-d.glass_size[1]/2-3,z+1.1],[x-6,y-d.glass_size[1]/2-7,z+.8]],4.5);
  ribbon(group,[[x+8,y-d.glass_size[1]/2,z+1.2],[x+9,y-d.glass_size[1]/2-3,z+1.1],[x+9,y-d.glass_size[1]/2-7,z+.8]],3.2);
}
function detailedBattery(group) {
  const b=parameters.battery,[x,y]=b.center,z=b.z;
  box(group,[b.size[0],b.size[1],b.size[2]],[x,y,z+b.size[2]/2],mats.white,1.8);
  box(group,[b.size[0]-.8,b.size[1]-.8,.12],[x,y,z+b.size[2]-.08],mats.tape,1.5);
  label(group,['LiPo 1S','34 × 30 × 3.4','CAPACITY TBD'],22,11,[x,y,z+b.size[2]+.03],true,'#263d3b','#e6f1dc');
  ribbon(group,[[x,y+b.size[1]/2,z+b.size[2]/2],[x+2,y+b.size[1]/2+2,z+b.size[2]/2],[x+6,y+b.size[1]/2+3,z+b.size[2]/2]],1.2);
  box(group,[1,1.2,.8],[x+5,y+b.size[1]/2+3,z+b.size[2]/2],mats.red,.15);box(group,[1,1.2,.8],[x+6.2,y+b.size[1]/2+3,z+b.size[2]/2],mats.black,.15);
}
function detailedAudio(group) {
  const e=parameters.electronics.find(e=>e.id==='audio'),[x,y]=e.center,z=e.z;
  board(group,e.size[0],e.size[1],1,[x,y,z],mats.pcb,[[e.size[0]/2-2,e.size[1]/2-2,1]]);chip(group,x,y+2,z+1,7,5);chip(group,x-5,y-5,z+1,3,2);for(let i=0;i<5;i++)passive(group,x-5+i*2,y+7,z+1);label(group,['AUDIO','DAC + HP'],13,6,[x,y,z+1.7],true,null,'#dcebe2');
  cylinder(group,2.3,4,[x,y-e.size[1]/2-1.5,z+2.6],mats.silver,32);cylinder(group,1.5,4.1,[x,y-e.size[1]/2-1.5,z+2.6],mats.black,32);
}
function detailedInterface(group) {
  const e=parameters.electronics.find(e=>e.id==='interface_pcb'),[x,y]=e.center,z=e.z;
  board(group,e.size[0],e.size[1],e.size[2],[x,y,z],mats.pcb,[[e.size[0]/2-2,e.size[1]/2-2,1]]);chip(group,x-8,y,z+.8,5,3);chip(group,x+2,y+3,z+.8,4,2.5);for(let i=0;i<10;i++)passive(group,x-12+(i%5)*5,y-5+Math.floor(i/5)*8,z+.8,.9,.6);label(group,['CUSTOM I/O','SPI + I2C'],12,5,[x,y,z+1.1],true,null,'#dcebe2');
}
function detailedMicroSD(group) {
  const e=parameters.electronics.find(e=>e.id==='microsd'),[x,y]=e.center,z=e.z;
  board(group,e.size[0],e.size[1],.8,[x,y,z],mats.blue);box(group,[14,10,1.7],[x,y,z+1.25],mats.silver,.8);box(group,[12,8,.25],[x,y-1,z+2.12],mats.black,.5);box(group,[10,6,.35],[x,y+1,z+2.3],mats.blue,.3);for(let i=0;i<8;i++)box(group,[.55,4,.06],[x-3.5+i,y-1,z+2.5],mats.gold,.05);
}
function detailedZif(group,id) {
  const e=parameters.electronics.find(e=>e.id===id),[x,y]=e.center,z=e.z,contacts=id==='touch_zif'?6:15;
  box(group,[e.size[0],e.size[1],1],[x,y,z+.5],mats.black,.35);box(group,[e.size[0]-.7,e.size[1]-.8,.3],[x,y,z+1.05],mats.silver,.15);
  for(let i=0;i<contacts;i++)box(group,[.18,.9,.08],[x+(i-(contacts-1)/2)*(.5),y,z+1.23],mats.gold,.03);
  ribbon(group,[[x,y+e.size[1]/2,z+1.2],[x,y+e.size[1]/2+3,z+1.2],[x+1,y+e.size[1]/2+5,z+1]],id==='touch_zif'?3:4.5);
}
function detailedControl(group) { const e=parameters.electronics.find(e=>e.id==='control'),[x,y]=e.center,z=e.z;board(group,e.size[0],e.size[1],.7,[x,y,z],mats.pcb);chip(group,x,y,z+.7,5,2.2); }
detailedDisplay(parts.get('touch_glass'));detailedBattery(parts.get('battery'));detailedAudio(parts.get('audio'));detailedInterface(parts.get('interface_pcb'));detailedMicroSD(parts.get('microsd'));detailedZif(parts.get('display_zif'),'display_zif');detailedZif(parts.get('touch_zif'),'touch_zif');detailedControl(parts.get('control'));
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
    group.visible = groups[group.userData.group] && !hidden.has(id) && !(view === 'inside' && id === 'rear_shell');
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
  const spread = explode / 100;
  const compact = w < 480;
  const span = Math.max(compact ? 170 : 150, (view === 'inside' ? 85 : 94) / aspect) * (1 + spread * (aspect < 0.9 ? 0.55 : 0.17)) / zoom;
  camera.left = -span * aspect / 2; camera.right = span * aspect / 2;
  camera.top = span / 2; camera.bottom = -span / 2;
  camera.updateProjectionMatrix();
  orbit.rotation.set(pitch, yaw, 0, 'XYZ');
  orbit.position.y = compact ? 8 : 0;
  updateVisibility();
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
  document.getElementById('viewname').textContent = view === 'inside' ? 'Inside / rear shell removed' : explode ? 'Exploded assembly' : 'Touchscreen / T01';
  invalidate();
}
document.querySelectorAll('[data-view]').forEach(b => b.onclick = () => {
  view = b.dataset.view;
  if (view === 'front') { yaw = 0; pitch = 0; }
  else if (view === 'back') { yaw = Math.PI; pitch = 0; }
  else if (view === 'inside') { yaw = Math.PI + 0.24; pitch = -0.16; groups.components = true; for (const [id, p] of parts) if (p.userData.group === 'components') hidden.delete(id); }
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
  getState: () => ({variant:'T01_concept',view,explode,zoom,visible:visibleParts().length,hidden:[...hidden]}),
  getInspection: () => ({parameters,ids:[...parts.keys()],screen:{width:aw,height:ah,parent: lcd.parent.name},validated:data.validation.passed}),
  render:invalidate
};
