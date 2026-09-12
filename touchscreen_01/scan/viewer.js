import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const data=JSON.parse(document.querySelector('#data').textContent);
const canvas=document.querySelector('canvas'),scene=new THREE.Scene();scene.background=new THREE.Color('#e7eeeb');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));
const camera=new THREE.PerspectiveCamera(35,1,.1,1000);camera.up.set(0,0,1);camera.position.set(80,-125,130);
const controls=new OrbitControls(camera,canvas);controls.target.set(0,-8,2);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight('#ffffff','#54685f',2));
const light=new THREE.DirectionalLight('#fff8e8',3);light.position.set(-30,30,80);scene.add(light);
const decode=(s,Type)=>new Type(Uint8Array.from(atob(s),c=>c.charCodeAt(0)).buffer);
const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(decode(data.vertices,Float32Array),3));geometry.setIndex(new THREE.BufferAttribute(decode(data.faces,Uint32Array),1));geometry.computeVertexNormals();
const mat=new THREE.MeshStandardMaterial({color:'#8d9c94',roughness:.75,side:THREE.DoubleSide});
scene.add(new THREE.Mesh(geometry,mat));
const grid=new THREE.GridHelper(100,20,'#849c90','#bdcdc4');grid.rotation.x=Math.PI/2;grid.position.z=-1.2;scene.add(grid);
document.querySelector('#wire').onchange=e=>mat.wireframe=e.target.checked;
document.querySelector('#grid').onchange=e=>grid.visible=e.target.checked;
for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>{
 const v=button.dataset.view;camera.position.set(...(v==='rear'?[0,-8,150]:v==='side'?[0,-160,8]:[80,-125,130]));controls.target.set(0,-8,2);controls.update();
};
function draw(){requestAnimationFrame(draw);const w=canvas.clientWidth,h=canvas.clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();controls.update();renderer.render(scene,camera);}
draw();window.T01_SCAN={units:'mm',triangles:data.triangle_count,textured:false};
