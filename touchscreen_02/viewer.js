import * as THREE from 'three';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
const data=window.STUDY_DATA, canvas=document.querySelector('#view'),stage=document.querySelector('#stage');
try {
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(36,1,1,1000);camera.up.set(0,1,0);
const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x809397,2.4));
for(const pos of [[100,130,-180],[-100,40,120]]){const light=new THREE.DirectionalLight(0xffffff,2);light.position.set(...pos);scene.add(light);}
const groups=new Map();
function vertices(encoded){const s=atob(encoded),a=new Uint8Array(s.length);for(let i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return new Float32Array(a.buffer);}
for(const part of data.parts){
 const group=new THREE.Group();group.userData=part;scene.add(group);groups.set(part.id,group);
 for(const batch of part.batches){const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(vertices(batch.positions),3));geo.computeVertexNormals();const color=batch.color_linear?new THREE.Color(...batch.color_linear):new THREE.Color(batch.color);group.add(new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color,roughness:.65,metalness:.15,transparent:part.reserve,opacity:part.reserve?.3:1,depthWrite:!part.reserve,side:THREE.DoubleSide})));}
 group.visible=!part.reserve;
 if(!part.reserve){const label=document.createElement('label'),check=document.createElement('input');check.type='checkbox';check.checked=true;check.dataset.part=part.id;label.append(check,document.createTextNode(' '+part.id.replaceAll('_',' ')));document.querySelector('#parts').append(label);check.addEventListener('change',()=>{group.visible=check.checked;});}
}
function outline(w,l,h,color){const edge=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w,l,h)),new THREE.LineBasicMaterial({color,transparent:true,opacity:.55}));edge.position.z=h/2;scene.add(edge);}
outline(64,128,8.3,0x367092);outline(60.8,124.8,7.2,0x3d9075);
// One illustrative UI on the front of the single provisional screen envelope.
const ui=document.createElement('canvas');ui.width=640;ui.height=480;const c=ui.getContext('2d');c.fillStyle='#112e34';c.fillRect(0,0,640,480);c.fillStyle='#94cbb8';c.font='24px sans-serif';c.fillText('MYTUNAS / NOW PLAYING',35,55);c.fillStyle='#2e6963';c.fillRect(35,100,200,235);c.fillStyle='#b3dbc6';c.font='bold 90px sans-serif';c.fillText('m',83,248);c.fillStyle='#eef8f0';c.font='bold 31px sans-serif';c.fillText('Night walking',265,160);c.font='22px sans-serif';c.fillText('Your music, anywhere',265,205);c.fillText('02:14                 04:36',265,303);c.fillStyle='#83bfa9';c.fillRect(35,380,570,5);c.fillStyle='#fff';c.font='24px sans-serif';c.fillText('PREV                 PAUSE                 NEXT',35,439);
const texture=new THREE.CanvasTexture(ui);texture.colorSpace=THREE.SRGBColorSpace;const screen=new THREE.Mesh(new THREE.PlaneGeometry(48.96,36.72),new THREE.MeshBasicMaterial({map:texture,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1}));screen.rotation.y=Math.PI;screen.position.set(0,35,.50);groups.get('startek_envelope').add(screen);
const poses={iso:[125,130,-185],front:[0,0,-235],rear:[0,0,235],side:[235,0,4],bottom:[0,-235,4]};
function view(name){camera.up.set(...(name==='bottom'?[0,0,-1]:[0,1,0]));camera.position.set(...poses[name]);controls.target.set(0,0,4);controls.update();}
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));view('iso');
document.querySelector('#reserves').onchange=e=>{for(const g of groups.values())if(g.userData.reserve)g.visible=e.target.checked;};
document.querySelector('#explode').oninput=e=>{const t=Number(e.target.value)/100;for(const [id,g] of groups){const layer=id==='startek_envelope'?-32:id==='interface_envelope'||id==='microsd_nominal'?28:0;g.position.z=layer*t;}};
document.querySelector('#check').textContent=data.report.nominal_packing_passed?'Checked: no nominal component or reserved-volume overlaps. Mounts, seals and final battery pack remain unverified.':'Packing check failed.';
function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}new ResizeObserver(resize).observe(stage);resize();
function render(){requestAnimationFrame(render);controls.update();renderer.render(scene,camera);}render();
window.PACKING={report:data.report,inspect:()=>[...groups].map(([id,g])=>{const b=new THREE.Box3().setFromObject(g);return {id,visible:g.visible,bounds:[b.min.toArray(),b.max.toArray()],expected:g.userData.bounds_mm};})};
}catch(e){const el=document.querySelector('#error');el.hidden=false;el.textContent='3D preview unavailable: '+e.message;throw e;}
