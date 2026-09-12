import assert from 'node:assert/strict';
import { chromium } from '../revision_04/node_modules/playwright/index.mjs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const root=dirname(fileURLToPath(import.meta.url));
const expected=JSON.parse(await readFile(join(root,'validation.json'),'utf8'));
const sha=async path=>createHash('sha256').update(await readFile(path)).digest('hex');
for(const [path,hash] of Object.entries(expected.source_sha256))assert.equal(await sha(join(root,path)),hash);
assert.equal(await sha(join(root,'parameters.json')),expected.parameter_sha256);
for(const [path,hash] of Object.entries(expected.dependency_sha256))assert.equal(await sha(join(root,'..',path)),hash);
const browser=await chromium.launch({executablePath:process.env.T01_BROWSER_PATH||'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',headless:true,args:['--enable-unsafe-swiftshader','--disable-background-networking']});
const errors=[],requests=[],checks=[],cameraChecks=[];
try {
 const page=await browser.newPage({viewport:{width:1200,height:950}});
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
 await page.goto(pathToFileURL(join(root,'preview.html')).href);
 await page.waitForFunction(()=>window.PACKING);
 const report=await page.evaluate(()=>PACKING.report);
 assert.deepEqual(report,expected);
 assert(report.passed);
 assert.equal(report.qualified_for_fabrication,false);
 assert.equal(report.screen_stock_confirmed,false);
 assert.deepEqual(report.exterior_mm,[64,128,8.3]);
 assert.equal(report.jack_edge,'bottom');assert.deepEqual(report.jack_axis,[0,-1,0]);
 assert.equal(report.vendor_dac_rotation_z_degrees,-90);
 assert(Math.abs(report.jack_mouth_mm[1]+63.6)<1e-6);
 assert(report.jack_mouth_mm[0]>0 && report.jack_mouth_mm[0]<32);
 for(const name of ['physical_collisions','reserve_collisions','port_wall_obstructions','outside_exterior'])assert.deepEqual(report[name],[]);
 assert(report.mesh_checks.every(c=>c.watertight&&c.winding_consistent&&c.bodies===1));
 assert(report.nominal_support_contacts.every(c=>c.gap_mm<=.005));
 const parts=await page.evaluate(()=>PACKING.inspect());
 assert.equal(await page.locator('#covers').isChecked(),false);
 assert(parts.filter(p=>p.kind==='cover').every(p=>!p.visible),'Ports must be exposed on first load');
 assert.equal(report.service_design.metal_threaded_inserts,13);
 assert.equal(parts.filter(p=>/^cell_[AB]_envelope$/.test(p.id)).length,2);
 for(const part of parts){
  assert.equal(part.physicalMeshes,part.expectedMeshes,`Duplicated or missing physical geometry: ${part.id}`);
  for(let side=0;side<2;side++)for(let axis=0;axis<3;axis++)assert(Math.abs(part.bounds[side][axis]-part.expected[side][axis])<.09,`Mesh differs from CAD: ${part.id}`);
 }
 async function capture(name,closeup=false){
  await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const pixels=await page.evaluate(()=>{
   const c=document.querySelector('#view'),g=c.getContext('webgl2'),p=new Uint8Array(c.width*c.height*4);
   g.readPixels(0,0,c.width,c.height,g.RGBA,g.UNSIGNED_BYTE,p);
   let count=0,minX=c.width,maxX=0,minY=c.height,maxY=0;
   for(let i=0;i<p.length;i+=4)if(p[i+3]>20){count++;const x=i/4%c.width,y=Math.floor(i/4/c.width);minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}
   return {count,minX,maxX,minY,maxY,w:c.width,h:c.height};
  });
  assert(pixels.count>2000,`Blank ${name}`);
  if(!closeup)assert(pixels.minX>0&&pixels.maxX<pixels.w-1&&pixels.minY>0&&pixels.maxY<pixels.h-1,`Clipped ${name}`);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Overflow ${name}`);
  await page.screenshot({path:join(root,name),fullPage:true});checks.push({name,pixels});
 }
 const cameraState=()=>page.evaluate(()=>PACKING.cameraState());
 function sameCamera(before,after,label){
  for(const key of Object.keys(before)){
   const a=Array.isArray(before[key])?before[key]:[before[key]],b=Array.isArray(after[key])?after[key]:[after[key]];
   a.forEach((n,i)=>assert(Math.abs(n-b[i])<1e-6,`${label} changed camera ${key}`));
  }
 }
 async function settleOrbit(){
  await page.evaluate(async()=>{
   let previous,stable=0;
   for(let i=0;i<600;i++){
    await new Promise(requestAnimationFrame);
    const state=Object.values(PACKING.cameraState()).flat();
    stable=previous&&state.every((n,j)=>Math.abs(n-previous[j])<1e-8)?stable+1:0;
    if(stable>=3)return;
    previous=state;
   }
   throw new Error('Orbit damping did not settle');
  });
 }
 async function persistentCamera(label){
  const initial=await cameraState(),box=await page.locator('#view').boundingBox();
  const x=box.x+box.width*.5,y=box.y+box.height*.45;
  // Real pointer orbit, wheel zoom and right-button pan reproduce the bug.
  await page.mouse.move(x,y);await page.mouse.down();await page.mouse.move(x+50,y+30,{steps:8});await page.mouse.up();
  await page.mouse.wheel(0,-100);
  await page.mouse.down({button:'right'});await page.mouse.move(x+70,y+40,{steps:4});await page.mouse.up({button:'right'});
  await settleOrbit();const before=await cameraState();assert.notDeepEqual(before,initial,'Gesture did not move camera');
  for(const value of ['25','70','35','0']){
   await page.locator('#explode').fill(value);await settleOrbit();sameCamera(before,await cameraState(),`${label}: explode ${value}`);
   const dac=(await page.evaluate(()=>PACKING.inspect())).find(p=>p.id==='audio');
   assert(Math.abs(dac.bounds[0][2]-dac.expected[0][2]-16*Number(value)/100)<.09,'Slider must still move parts');
  }
  for(const selector of ['#covers','#reserves','[data-part="front_bezel"]']){
   const control=page.locator(selector),original=await control.isChecked();
   for(const checked of [!original,original]){await control.setChecked(checked);await settleOrbit();sameCamera(before,await cameraState(),`${label}: ${selector}`);}
  }
  cameraChecks.push({label,orbit_pan_zoom_preserved:true,slider_moves_parts:true});
 }
 await capture('preview_iso.png');
 for(const view of ['front','rear','inside','side','bottom']){await page.locator(`[data-view="${view}"]`).click();await capture(`preview_${view}.png`);}
 await page.locator('#covers').uncheck();await capture('preview_ports_open.png');
 assert((await page.evaluate(()=>PACKING.inspect())).filter(p=>p.kind==='cover').every(p=>!p.visible));
 for(const port of ['usb','sd','jack']){
  await page.locator(`[data-view="${port}"]`).click();await capture(`preview_port_${port}.png`,true);
  assert.equal(await page.locator('#covers').isChecked(),false);
  const open=await page.locator('#view').screenshot();
  await page.locator('#covers').check();
  await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const closed=await page.locator('#view').screenshot();
  assert(!open.equals(closed),`Port cover has no visible effect: ${port}`);
  await page.locator('#covers').uncheck();
 }
 await page.locator('[data-view="iso"]').click();
 await persistentCamera('desktop');
 await page.locator('#reserves').check();await page.locator('#explode').fill('100');
 // An explicit preset frames the requested assembly for the reference image.
 await page.locator('[data-view="iso"]').click();await capture('preview_exploded.png');
 const beforeResize=await cameraState();
 await page.setViewportSize({width:390,height:844});await settleOrbit();sameCamera(beforeResize,await cameraState(),'Viewport resize');
 await page.locator('[data-view="iso"]').click();await capture('preview_mobile.png');
 await persistentCamera('mobile');
 await page.locator('[data-part="touch_glass"]').uncheck();
 assert.equal((await page.evaluate(()=>PACKING.inspect())).find(p=>p.id==='touch_glass').visible,false);
 await page.locator('#reset').click();await page.locator('[data-view="inside"]').click();await capture('preview_mobile_inside.png');
 // The old Model 02 entry must serve the selected layout instead of T02.
 await page.goto(pathToFileURL(join(root,'../touchscreen_01/preview.html')).href);
 await page.waitForFunction(()=>window.PACKING?.report?.model==='Model 02 / selected touchscreen layout');
 assert(page.url().endsWith('/touchscreen_02/preview.html'));
 assert.equal(await page.evaluate(()=>PACKING.report.jack_edge),'bottom');
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 await writeFile(join(root,'viewer_validation.json'),JSON.stringify({passed:true,model:report.model,parameter_sha256:report.parameter_sha256,geometry:parts,jack_mouth_mm:report.jack_mouth_mm,legacy_T02_redirect:true,cameraChecks,viewport_preserves_camera:true,errors,externalRequests:requests,checks},null,2)+'\n');
 console.log('PASS: CAD mesh agreement, desktop/mobile views, persistent orbit/pan/zoom across slider/options/resize and legacy redirect');
} finally {await browser.close();}
