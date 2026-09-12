import * as THREE from 'three';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import {RoomEnvironment} from 'three/examples/jsm/environments/RoomEnvironment.js';
const data=window.STUDY_DATA,canvas=document.querySelector('#view'),stage=document.querySelector('#stage');
try {
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;renderer.outputColorSpace=THREE.SRGBColorSpace;
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(36,1,1,1500);camera.up.set(0,1,0);
const pmrem=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();scene.environment=pmrem.fromScene(room,.04).texture;room.dispose();pmrem.dispose();
const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x71808d,1.25));
for(const pos of [[100,130,-180],[-100,40,120]]){const light=new THREE.DirectionalLight(0xffffff,2.4);light.position.set(...pos);scene.add(light);}
const groups=new Map(),checks=new Map();let current='iso';
function vertices(encoded){const s=atob(encoded),a=new Uint8Array(s.length);for(let i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return new Float32Array(a.buffer);}
const partOrder={structure:0,component:1,support:2,cover:3,seal:4,fastener:5,reserve:6};
for(const part of [...data.parts].sort((a,b)=>partOrder[a.kind]-partOrder[b.kind])){
 const group=new THREE.Group();group.userData=part;scene.add(group);groups.set(part.id,group);
 for(const batch of part.batches){const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(vertices(batch.positions),3));geo.computeVertexNormals();const color=batch.color_linear?new THREE.Color(...batch.color_linear):new THREE.Color(batch.color);const metal=(part.kind==='structure'&&part.id!=='midframe'||part.kind==='fastener'||part.id.startsWith('dac_retainer_')||part.id==='microsd_socket')&&batch.color!=='#314655';group.add(new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color,roughness:metal?.23:.7,metalness:metal?.94:.04,envMapIntensity:metal?1.2:.65,transparent:part.reserve,opacity:part.reserve?.24:1,depthWrite:!part.reserve,side:THREE.DoubleSide})));}
 group.visible=!part.reserve&&part.kind!=='cover';
 if(!part.reserve){const label=document.createElement('label'),check=document.createElement('input');check.type='checkbox';check.checked=group.visible;check.dataset.part=part.id;label.title=part.source+' / '+part.bounds_mm[0].map((v,i)=>(part.bounds_mm[1][i]-v).toFixed(2)).join(' × ')+' mm';label.append(check,document.createTextNode(' '+part.label));document.querySelector('#parts').append(label);checks.set(part.id,check);check.addEventListener('change',()=>{group.visible=check.checked;});}
}
const ui=document.createElement('canvas');ui.width=640;ui.height=480;const c=ui.getContext('2d');c.fillStyle='#112e34';c.fillRect(0,0,640,480);c.fillStyle='#94cbb8';c.font='24px sans-serif';c.fillText('MYTUNAS / NOW PLAYING',35,55);c.fillStyle='#2e6963';c.fillRect(35,100,200,235);c.fillStyle='#b3dbc6';c.font='bold 90px sans-serif';c.fillText('m',83,248);c.fillStyle='#eef8f0';c.font='bold 31px sans-serif';c.fillText('Night walking',265,160);c.font='22px sans-serif';c.fillText('Your music, anywhere',265,205);c.fillText('02:14                 04:36',265,303);c.fillStyle='#83bfa9';c.fillRect(35,380,570,5);c.fillStyle='#fff';c.font='24px sans-serif';c.fillText('PREV                 PAUSE                 NEXT',35,439);
const texture=new THREE.CanvasTexture(ui);texture.colorSpace=THREE.SRGBColorSpace;const screen=new THREE.Mesh(new THREE.PlaneGeometry(48.96,36.72),new THREE.MeshBasicMaterial({map:texture,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1}));screen.rotation.y=Math.PI;screen.position.set(0,35,.50);groups.get('touch_glass').add(screen);
const poses={iso:[125,130,-185],front:[0,0,-235],rear:[0,0,235],inside:[95,100,220],side:[235,0,4],bottom:[0,-235,4],usb:[1,0,0],sd:[-1,0,0],jack:[0,-1,0]};
const portIds={usb:'usb',sd:'microsd',jack:'jack'};
function setVisible(id,on){groups.get(id).visible=on;if(checks.has(id))checks.get(id).checked=on;}
// Reframe only for an explicit view preset or Reset. Model options and resize
// preserve the user-controlled orbit, pan target and zoom.
function fit(){
 scene.updateMatrixWorld(true);const box=new THREE.Box3();
 for(const g of groups.values())if(g.visible)box.union(new THREE.Box3().setFromObject(g));
 if(portIds[current]){const p=new THREE.Vector3(...data.report.ports[portIds[current]].center);const size=current==='jack'?new THREE.Vector3(14,4,11):new THREE.Vector3(4,19,11);box.setFromCenterAndSize(p,size);}
 if(box.isEmpty())return;const center=box.getCenter(new THREE.Vector3()),dir=new THREE.Vector3(...poses[current]).normalize();
 camera.up.set(...(current==='bottom'||portIds[current]?[0,0,-1]:[0,1,0]));camera.position.copy(center).addScaledVector(dir,300);camera.lookAt(center);camera.updateMatrixWorld();
 const inv=camera.quaternion.clone().invert(),tanV=Math.tan(THREE.MathUtils.degToRad(camera.fov/2)),tanH=tanV*camera.aspect;let distance=20;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const q=new THREE.Vector3(x,y,z).sub(center).applyQuaternion(inv);distance=Math.max(distance,Math.abs(q.x)/tanH+q.z,Math.abs(q.y)/tanV+q.z);}
 camera.position.copy(center).addScaledVector(dir,distance*1.15+3);controls.target.copy(center);controls.update();
}
function view(name){current=name;
 const open=name==='inside';for(const [id,g] of groups)if(['rear_shell','rear_liner','rear_gasket'].includes(id)||id.startsWith('case_screw_')||id.startsWith('dac_retainer_')||id.startsWith('dac_rear_screw_'))setVisible(id,!open);
 if(portIds[name]){document.querySelector('#covers').checked=false;for(const [id,g] of groups)if(g.userData.kind==='cover')setVisible(id,false);}
 document.querySelector('#view-note').textContent=portIds[name]?({usb:'USB-C · right edge',sd:'microSD · left edge',jack:'Headphones · bottom edge'})[name]+' / covers removed':open?'Rear removed · service access':'Drag to rotate · scroll to zoom';
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===name)));fit();
}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
document.querySelector('#reserves').onchange=e=>{for(const g of groups.values())if(g.userData.reserve)g.visible=e.target.checked;};
document.querySelector('#covers').onchange=e=>{for(const [id,g] of groups)if(g.userData.kind==='cover')setVisible(id,e.target.checked);};
document.querySelector('#explode').oninput=e=>{const t=Number(e.target.value)/100;for(const [id,g] of groups){g.position.set(0,0,g.userData.explode*t);if(id==='usb_cover')g.position.set(12*t,0,0);if(id==='sd_cover')g.position.set(-12*t,0,0);if(id==='jack_cover')g.position.set(0,-12*t,0);}};
document.querySelector('#reset').onclick=()=>{document.querySelector('#explode').value=0;document.querySelector('#reserves').checked=false;document.querySelector('#covers').checked=false;for(const [id,g] of groups){g.position.set(0,0,0);setVisible(id,!g.userData.reserve&&g.userData.kind!=='cover');}view('iso');};
document.querySelector('#check').textContent=data.report.passed?`${data.parts.filter(p=>!p.reserve).length} physical part groups. CAD fit and assembly-access checks passed. Samples, tolerances and ingress tests remain outstanding.`:'Fit check failed.';
function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}new ResizeObserver(resize).observe(stage);resize();view('iso');
function render(){requestAnimationFrame(render);controls.update();renderer.render(scene,camera);}render();
window.PACKING={report:data.report,parameters:data.parameters,cameraState:()=>({position:camera.position.toArray(),target:controls.target.toArray(),quaternion:camera.quaternion.toArray(),up:camera.up.toArray(),zoom:camera.zoom}),inspect:()=>[...groups].map(([id,g])=>{const b=new THREE.Box3().setFromObject(g);return {id,visible:g.visible,kind:g.userData.kind,physicalMeshes:g.children.filter(c=>c!==screen).length,expectedMeshes:g.userData.batches.length,bounds:[b.min.toArray(),b.max.toArray()],expected:g.userData.bounds_mm};})};
}catch(e){const el=document.querySelector('#error');el.hidden=false;el.textContent='3D preview unavailable: '+e.message;throw e;}
