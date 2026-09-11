import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { STLExporter } from 'three/addons/exporters/STLExporter.js';
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
function board(group, width, height, thickness, position, mat, holes = []) {
  const shape = new THREE.Shape();
  const r = 0.7, x = -width / 2, y = -height / 2;
  shape.moveTo(x + r, y); shape.lineTo(-x - r, y); shape.quadraticCurveTo(-x, y, -x, y + r);
  shape.lineTo(-x, -y - r); shape.quadraticCurveTo(-x, -y, -x - r, -y);
  shape.lineTo(x + r, -y); shape.quadraticCurveTo(x, -y, x, -y - r);
  shape.lineTo(x, y + r); shape.quadraticCurveTo(x, y, x + r, y);
  for (const [hx, hy, radius] of holes) {
    const hole = new THREE.Path(); hole.absarc(hx, hy, radius, 0, Math.PI * 2, true); shape.holes.push(hole);
  }
  const geometry = new THREE.ExtrudeGeometry(shape, { depth: thickness, bevelEnabled: false, curveSegments: 12 });
  const pcb = mesh(group, geometry, mat, position);
  for (const [hx, hy, radius] of holes) {
    ring(group, radius + 0.5, radius, [position[0] + hx, position[1] + hy, position[2] + thickness + 0.015], mats.gold);
    const bottom = ring(group, radius + 0.5, radius, [position[0] + hx, position[1] + hy, position[2] - 0.015], mats.gold);
    bottom.rotation.x = Math.PI;
  }
  return pcb;
}
function passive(group, x, y, z, width = 1.4, length = 0.75, mat = mats.ceramic) {
  box(group, [width, length, 0.45], [x, y, z + 0.225], mat, 0.08);
  for (const dx of [-width * 0.4, width * 0.4]) box(group, [width * 0.22, length + 0.05, 0.48], [x + dx, y, z + 0.24], mats.solder);
}
function chip(group, x, y, z, width, height) {
  box(group, [width, height, 0.65], [x, y, z + 0.325], mats.black, 0.12);
  for (let i = 0; i < 5; i++) for (const side of [-1, 1]) {
    box(group, [0.7, 0.25, 0.18], [x + side * (width / 2 + 0.2), y + (i - 2) * height / 5, z + 0.1], mats.solder);
  }
  cylinder(group, 0.16, 0.02, [x - width / 2 + 0.45, y + height / 2 - 0.45, z + 0.66], mats.dark, 12);
}
function ribbon(group, points, width) {
  const curve = new THREE.CatmullRomCurve3(points.map(p => new THREE.Vector3(...p)));
  const vertices = [], indices = [];
  for (let i = 0; i <= 48; i++) {
    const p = curve.getPoint(i / 48);
    vertices.push(p.x - width / 2, p.y, p.z, p.x + width / 2, p.y, p.z);
    if (i < 48) { const n = i * 2; indices.push(n, n + 1, n + 2, n + 1, n + 3, n + 2); }
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geometry.setIndex(indices); geometry.computeVertexNormals();
  const mat = mats.flex.clone(); mat.side = THREE.DoubleSide;
  mesh(group, geometry, mat);
  for (let i = 0; i < 8; i++) {
    path(group, curve.getPoints(24).map(p => [p.x + (i - 3.5) * 0.5, p.y, p.z + 0.045]), 0.04, mats.copper);
  }
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

function display(group) {
  const d = parameters.display, [x, y] = d.center, z = d.z;
  board(group, d.size[0], d.size[1], 0.5, [x, y, z + 2.3], mats.pcb, [[-23, -17, 1], [23, -17, 1], [-23, 17, 1], [23, 17, 1]]);
  box(group, [47, 35.8, 1.7], [x, y, z + 1.45], mats.silver, 0.35);
  box(group, [44.4, 33.4, 0.7], [x, y, z + 0.35], mats.black, 0.25);
  const screenMap = texture(640, 480, (ctx, w, h) => {
    ctx.fillStyle = '#101c24'; ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = '#ecf5f3'; ctx.font = '20px Arial'; ctx.fillText('NOW PLAYING', 26, 38);
    ctx.strokeStyle = '#c8ded7'; ctx.lineWidth = 3; ctx.strokeRect(558, 19, 45, 18);
    ctx.fillStyle = '#7cd9b5'; ctx.fillRect(562, 23, 32, 10); ctx.fillRect(605, 24, 4, 8);
    ctx.fillStyle = '#1f3949'; ctx.fillRect(26, 66, 212, 212);
    // Album artwork is drawn into the LCD texture and shares its physical plane.
    ctx.fillStyle = '#315b62'; ctx.fillRect(26, 166, 212, 112);
    ctx.fillStyle = '#eab571'; ctx.beginPath(); ctx.arc(175, 124, 34, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#193547'; ctx.beginPath(); ctx.moveTo(26, 218); ctx.lineTo(100, 135); ctx.lineTo(166, 218); ctx.fill();
    ctx.fillStyle = '#437977'; ctx.beginPath(); ctx.moveTo(74, 278); ctx.lineTo(179, 176); ctx.lineTo(238, 235); ctx.lineTo(238, 278); ctx.fill();
    ctx.fillStyle = '#eaf3f1'; ctx.font = 'bold 29px Arial'; ctx.fillText('Evening light', 263, 117, 350);
    ctx.fillStyle = '#9fbabf'; ctx.font = '22px Arial'; ctx.fillText('Local collection', 263, 156);
    ctx.fillStyle = '#72c5a8'; ctx.font = '17px monospace'; ctx.fillText('MP3  /  320 KBPS', 263, 218);
    ctx.fillStyle = '#38515a'; ctx.fillRect(27, 321, 586, 4);
    ctx.fillStyle = '#7cd9b5'; ctx.fillRect(27, 321, 226, 4); ctx.beginPath(); ctx.arc(253, 323, 6, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#acc3c9'; ctx.font = '18px monospace'; ctx.fillText('1:24', 27, 355); ctx.fillText('3:42', 569, 355);
    ctx.fillStyle = '#eaf3f1'; ctx.fillRect(307, 396, 8, 28); ctx.fillRect(325, 396, 8, 28);
    for (const [cx, direction] of [[218, -1], [422, 1]]) {
      ctx.beginPath(); ctx.moveTo(cx + direction * 12, 410); ctx.lineTo(cx - direction * 8, 397); ctx.lineTo(cx - direction * 8, 423); ctx.fill();
      ctx.fillRect(cx + direction * 14 - 2, 397, 4, 26);
    }
  });
  const lcd = surface(group, 40.8, 30.6, [x, parameters.display.window_y, z - 0.012], screenMap, false, false);
  lcd.name = 'lcd-active-surface'; lcd.userData.width = 40.8; lcd.userData.height = 30.6;
  label(group, ['ST7789', '240 x 320 / SPI', 'LCD MODULE'], 20, 8, [x, y, z + 2.815]);
  for (let i = 0; i < 8; i++) {
    box(group, [1.3, 2.8, 0.04], [x + (i - 3.5) * 2.54, y - 18.2, z + 2.81], mats.gold);
    path(group, [[x + (i - 3.5) * 2.54, y - 16.8, z + 2.81], [x + (i - 3.5) * 1.3, y - 12, z + 2.81]], 0.06, mats.copper);
  }
  ribbon(group, [[x + 20, y - 7, z + 2.82], [x + 23, y - 9, z + 2.85], [x + 24, y - 11, z + 2.4], [x + 23, y - 13, z + 1.5]], 4.4);
}

function wheel(parent) {
  const w = parameters.wheel, [x, y] = w.center;
  const group = new THREE.Group(); group.name = 'wheel-mechanism';
  group.position.z = w.backing_z - 1.6; parent.add(group);
  cylinder(group, 25.2, 0.55, [x, y, 3.05], mats.silver);
  cylinder(group, 23.8, 1.25, [x, y, 2.18], mats.dark);
  for (const dx of [-1, 1]) for (const dy of [-1, 1]) {
    box(group, [7.2, 9.8, 0.5], [x + dx * 23.6, y + dy * 23.2, 2.9], mats.silver, 0.5);
    cylinder(group, 1.05, 0.12, [x + dx * 24.5, y + dy * 24.2, 3.22], mats.dark);
  }
  cylinder(group, 22, 1.35, [x, y, 0.875], mats.wheel, 96);
  cylinder(group, 7.1, 1.42, [x, y, 0.87], mats.dark, 64);
  cylinder(group, 6.8, 1.43, [x, y, 0.855], mats.white, 64);
  const markings = texture(512, 512, ctx => {
    ctx.fillStyle = '#747d82'; ctx.font = 'bold 27px Arial'; ctx.textAlign = 'center'; ctx.fillText('MENU', 256, 74);
    const triangle = (x, y, d) => { ctx.beginPath(); ctx.moveTo(x + d * 9, y); ctx.lineTo(x - d * 7, y - 10); ctx.lineTo(x - d * 7, y + 10); ctx.fill(); };
    for (const [x, d] of [[65, -1], [447, 1]]) { triangle(x - d * 8, 256, d); triangle(x + d * 9, 256, d); ctx.fillRect(x + d * 21 - 1, 246, 3, 20); }
    triangle(244, 446, 1); ctx.fillRect(260, 435, 4, 22); ctx.fillRect(270, 435, 4, 22);
  });
  surface(group, 44, 44, [x, y, 0.187], markings);
  const flexMat = mats.flex.clone(); flexMat.side = THREE.DoubleSide;
  ring(group, 21.4, 8.0, [x, y, 3.35], flexMat);
  for (let i = 0; i < 24; i++) {
    const a = i * Math.PI / 12, r = 18.2;
    const segment = box(group, [0.18, 5.3, 0.035], [x + Math.sin(a) * r, y + Math.cos(a) * r, 3.38], mats.copper);
    segment.rotation.z = -a;
  }
  for (const [dx, dy] of [[0, 0], [15.5, 0], [-15.5, 0], [0, 15.5], [0, -15.5]]) {
    cylinder(group, 3.25, 0.3, [x + dx, y + dy, 3.6], mats.gold, 32);
    cylinder(group, 2.75, 0.4, [x + dx, y + dy, 3.91], mats.silver, 32);
  }
  chip(group, x + 10.5, y - 16, 3.45, 3.4, 4.6);
  label(group, ['CLICK WHEEL', '8P / 0.5'], 13, 5, [x - 6, y - 17, 3.45]);
  const fpc = parameters.electronics.find(b => b.id === 'fpc8');
  const bend = parameters.routing_reserves.find(r => r.id === 'clickwheel_flex');
  ribbon(parent, [[x - 15, y + 1, 3.42 + group.position.z], [fpc.center[0], bend.center[1] + 1.5, 4.3],
    [fpc.center[0], bend.center[1], 5.3], [fpc.center[0], bend.center[1] - 1.05, fpc.z + 2.04],
    [fpc.center[0], fpc.center[1] + 7.12, fpc.z + 2.04]], 4.4);
}

function battery(parent) {
  const b = parameters.battery, [bx, by] = b.center, z = b.z;
  // Rotate the complete pouch/label/PCM assembly, not just its bounding box.
  const group = new THREE.Group(); group.name = 'battery-pouch';
  group.position.set(bx, by, 0); group.rotation.z = THREE.MathUtils.degToRad(b.rotation_degrees); parent.add(group);
  const x = 0, y = 0, [w, h, d] = b.size;
  const foil = new THREE.MeshStandardMaterial({ color: '#bdc4cb', metalness: 0.86, roughness: 0.38 });
  const bump = texture(256, 256, (ctx, width, height) => {
    ctx.fillStyle = '#aaa'; ctx.fillRect(0, 0, width, height);
    for (let i = 0; i < 55; i++) {
      ctx.strokeStyle = `rgba(${i % 2 ? '230,230,230' : '50,50,50'},0.16)`;
      ctx.beginPath(); ctx.moveTo(i * 7 % width, 0); ctx.bezierCurveTo(i * 7 % width + 8, 75, i * 7 % width - 9, 180, i * 7 % width, height); ctx.stroke();
    }
  });
  bump.colorSpace = THREE.NoColorSpace; foil.bumpMap = bump; foil.bumpScale = 0.045;
  box(group, [w - 1.2, h - 1.4, d - 0.15], [x, y, z + d / 2], foil, 0.9);
  for (const dy of [-1, 1]) box(group, [w, 0.75, 0.24], [x, y + dy * (h / 2 - 0.4), z + d / 2], mats.silver, 0.1);
  box(group, [3.8, h - 0.7, d - 0.1], [x + w / 2 - 2, y, z + d / 2], mats.tape, 0.35);
  label(group, ['Li-ion Polymer', '503040   3.7 V', '600 mAh / 2.22 Wh', '+                 -'], 28, 16, [x - 2, y, z + d + 0.01], true, '#eef0ed', '#273139');
  const pocket = parameters.routing_reserves.find(r => r.id === 'battery_connector_pocket');
  const bridge = parameters.routing_reserves.find(r => r.id === 'upper_harness_bridge');
  const [cx, cy] = pocket.center;
  for (const [dx, mat] of [[0.7, mats.red], [-0.7, mats.black]]) {
    path(parent, [[bx + w / 2 - 1, by + h / 2 - 3 + dx, z + 1.9],
      [bx + w / 2 + 2.5, by + h / 2 - 3 + dx, z + 1.9], [bx + w / 2 + 2.5, bridge.center[1] + dx * 0.2, z + 1.9],
      [cx + dx, bridge.center[1] + dx * 0.2, z + 1.9],
      [cx + dx, cy - 3.5, z + 2.6], [cx + dx, cy - 2.6, z + 2.6]], 0.32, mat);
  }
  const connector = new THREE.Group(); connector.name = 'battery-connector'; parent.add(connector);
  box(connector, [4.2, 5.2, 2.9], [cx, cy, z + 2.6], mats.white, 0.3);
  box(connector, [3, 0.4, 0.7], [cx, cy - 2.62, z + 3.3], mats.dark);
  box(connector, [2.4, 1.8, 0.4], [cx, cy + 0.2, z + 4.1], mats.white);
}

function microsd(group) {
  const b = parameters.electronics.find(b => b.id === 'microsd'), [x, y] = b.center, z = b.z;
  const holes = Array.from({ length: 6 }, (_, i) => [-9, (i - 2.5) * 2.54, 0.48]);
  board(group, b.size[0], b.size[1], 0.85, [x, y, z], mats.blue, holes);
  box(group, [15.5, 14, 0.45], [x + 3.1, y, z + 1.1], mats.black, 0.25);
  // Open mouth, spring contacts, folded metal cage and an inserted card edge.
  for (const dy of [-6.8, 6.8]) box(group, [15.5, 0.35, 1.8], [x + 3.1, y + dy, z + 2.1], mats.silver);
  box(group, [0.35, 13.5, 1.8], [x - 4.5, y, z + 2.1], mats.silver);
  box(group, [15.5, 13.9, 0.25], [x + 3.1, y, z + 3.13], mats.silver, 0.1);
  box(group, [15, 11, 1.0], [x + 4.65, y, z + 1.95], mats.black, 0.18);
  for (let i = 0; i < 8; i++) {
    box(group, [1.8, 0.42, 0.12], [x - 4.6, y + (i - 3.5) * 1.05, z + 1.25], mats.gold);
    box(group, [0.8, 0.5, 0.15], [x - 5.6, y + (i - 3.5) * 1.05, z + 0.94], mats.solder);
  }
  for (const dx of [-1.5, 5.3]) for (const dy of [-5.8, 5.8]) {
    box(group, [2.4, 0.5, 0.025], [x + dx, y + dy, z + 3.27], mats.dark);
  }
  passive(group, x - 6.3, y - 5, z + 0.85, 1.4, 0.7);
  passive(group, x - 6.3, y + 4.8, z + 0.85, 1.4, 0.7);
  label(group, ['microSD', 'PUSH / LOCK'], 11, 5, [x + 3.3, y, z + 3.28], true, null, '#3e474c');
  label(group, ['SPI', '3V3'], 3, 4, [x - 6.3, y, z + 0.88]);
}

function adapter(group) {
  const b = parameters.electronics.find(b => b.id === 'fpc8'), [x, y] = b.center, z = b.z;
  const holes = Array.from({ length: 8 }, (_, i) => [(i - 3.5) * 2.54, -7.1, 0.5]);
  board(group, b.size[0], b.size[1], 1.6, [x, y, z], mats.pcb, holes);
  box(group, [8.1, 4, 1.55], [x, y + 5.1, z + 2.375], mats.white, 0.18);
  box(group, [5.3, 0.3, 0.42], [x, y + 7.12, z + 2.04], mats.black);
  box(group, [7.6, 1.2, 0.5], [x, y + 6.3, z + 3.2], mats.dark, 0.12);
  for (let i = 0; i < 8; i++) {
    box(group, [0.23, 1.1, 0.2], [x + (i - 3.5) * 0.5, y + 2.9, z + 1.73], mats.gold);
    path(group, [[x + (i - 3.5) * 0.5, y + 2.5, z + 1.62], [x + (i - 3.5) * 2.54, y - 4.5, z + 1.62], [x + (i - 3.5) * 2.54, y - 6.3, z + 1.62]], 0.07, mats.copper);
  }
  for (const dx of [-4.1, 4.1]) box(group, [1.2, 2.2, 0.18], [x + dx, y + 5, z + 1.7], mats.solder);
  label(group, ['8P / 0.5 mm'], 14, 3, [x, y - 1, z + 1.72]);
  label(group, ['1  2  3  4  5  6  7  8'], 21, 2.5, [x, y - 4.6, z + 1.72]);
  label(group, ['FPC ADAPTER', '8 CONTACTS'], 17, 7, [x, y, z - 0.015], false);
}

for (const spec of data.parts) {
  const group = new THREE.Group(); group.name = spec.id; group.userData = spec;
  parts.set(spec.id, group); assembly.add(group);
  if (spec.positions) {
    const mat = spec.id === 'clear_lens_reference'
      ? new THREE.MeshPhysicalMaterial({ color: '#d7f0f5', metalness: 0, roughness: 0.1, transparent: true, opacity: 0.045, depthWrite: false, envMapIntensity: 0.35 })
      : material(spec.color, 0.05, 0.5);
    imported(group, spec.positions, mat);
    if (spec.engraving_positions) {
      const engraving = imported(group, spec.engraving_positions, material('#59686c', 0.08, 0.72));
      engraving.name = 'rear-branding-recess';
    }
  } else if (data.vendor[spec.id]) {
    for (const batch of data.vendor[spec.id]) {
      const color = new THREE.Color().setRGB(...batch.color, THREE.LinearSRGBColorSpace);
      const saturation = Math.max(...batch.color) - Math.min(...batch.color);
      const brightness = Math.max(...batch.color);
      const metallic = brightness > 0.24 && saturation < 0.12 || batch.color[0] > batch.color[2] * 1.4;
      const mat = new THREE.MeshStandardMaterial({ color, metalness: metallic ? 0.7 : 0.05, roughness: metallic ? 0.32 : 0.64, side: THREE.DoubleSide });
      imported(group, batch.positions, mat);
    }
  } else ({ display_envelope: display, clickwheel_envelope: wheel, battery_envelope: battery, microsd, fpc8: adapter })[spec.id](group);
}

// Silkscreen and shield printing are separate surfaces on the manufacturer CAD.
const xiao = parts.get('xiao'), xb = parameters.electronics.find(b => b.id === 'xiao');
label(xiao, ['Seeed Studio', 'XIAO ESP32-S3'], 9.2, 8.2, [xb.center[0] - 1.53, xb.center[1], xb.z + 3.265], true, '#c0c6cb', '#30373b');
const dac = parts.get('dac'), db = parameters.electronics.find(b => b.id === 'dac');
label(dac, ['Adafruit', 'TLV320DAC3100', 'I2S DAC + HPA'], 18, 10,
  [db.center[0], db.center[1] - 3.55, db.z - 0.015], false);
label(dac, ['VIN GND BCK WSEL DIN'], 21, 3,
  [db.center[0] - 0.2, db.center[1] - 12.25, db.z + 1.585]);

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
  const span = Math.max(compact ? 201 : 181, (view === 'inside' ? 85 : 94) / aspect) * (1 + spread * (aspect < 0.9 ? 0.55 : 0.17)) / zoom;
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
  document.getElementById('viewname').textContent = view === 'inside' ? 'Inside / rear shell removed' : explode ? 'Exploded assembly' : 'Compact construction';
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
window.FORM01 = {
  getState: () => ({ variant: 'P04_compact', yaw, pitch, zoom, explode, view, groups: { ...groups }, visible: visibleParts().length, hidden: [...hidden] }),
  getInspection: () => {
    scene.updateMatrixWorld(true);
    const lcd = assembly.getObjectByName('lcd-active-surface');
    const branding = assembly.getObjectByName('rear-branding-recess');
    return {
      layout: { body: parameters.body, battery: parameters.battery,
        wheelSeatOffset: assembly.getObjectByName('wheel-mechanism').position.z,
        electronics: parameters.electronics, routing: parameters.routing_reserves,
        batteryRotation: assembly.getObjectByName('battery-pouch').rotation.z,
        connectorBounds: (() => {
          const b = new THREE.Box3();
          assembly.getObjectByName('battery-connector').traverse(o => {
            if (!o.isMesh) return;
            o.geometry.computeBoundingBox();
            b.union(o.geometry.boundingBox.clone().translate(o.position));
          });
          return { min: b.min.toArray(), max: b.max.toArray() };
        })() },
      branding: { name: parameters.branding.name, parent: branding.parent.name,
        visible: branding.parent.visible, depth: parameters.branding.depth,
        bounds: (() => { branding.geometry.computeBoundingBox(); const b = branding.geometry.boundingBox; return { min: b.min.toArray(), max: b.max.toArray() }; })(),
        world: branding.getWorldPosition(new THREE.Vector3()).toArray() },
      screen: { parent: lcd.parent.name, localZ: lcd.position.z, width: lcd.userData.width, height: lcd.userData.height, world: lcd.getWorldPosition(new THREE.Vector3()).toArray(), depthTest: lcd.material.depthTest, visible: lcd.parent.visible },
      parts: [...parts.values()].map(p => ({ id: p.name, source: p.userData.source, visible: p.visible, meshes: (() => { let n = 0; p.traverse(o => { if (o.isMesh) n++; }); return n; })(), offset: p.position.z })),
      triangles: renderer.info.render.triangles,
    };
  },
  exportReferenceSTL: id => {
    const part = parts.get(id);
    if (!part || part.userData.group !== 'components') throw new Error(`Not a component: ${id}`);
    const copy = part.clone(true);
    copy.position.set(0, 0, 0);
    const excluded = [];
    copy.traverse(o => { if (o.userData.surface || o.userData.outline) excluded.push(o); });
    for (const o of excluded) o.removeFromParent();
    copy.updateMatrixWorld(true);
    const binary = new STLExporter().parse(copy, { binary: true });
    const bytes = new Uint8Array(binary.buffer), chunks = [];
    for (let i = 0; i < bytes.length; i += 32768) chunks.push(String.fromCharCode(...bytes.subarray(i, i + 32768)));
    return btoa(chunks.join(''));
  },
  render: invalidate,
};
