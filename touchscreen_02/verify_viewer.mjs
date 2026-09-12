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
const errors=[],requests=[],checks=[];
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
 assert.equal(parts.filter(p=>/^cell_[AB]_envelope$/.test(p.id)).length,2);
 for(const part of parts){
  assert.equal(part.physicalMeshes,part.expectedMeshes,`Duplicated or missing physical geometry: ${part.id}`);
  for(let side=0;side<2;side++)for(let axis=0;axis<3;axis++)assert(Math.abs(part.bounds[side][axis]-part.expected[side][axis])<.09,`Mesh differs from CAD: ${part.id}`);
 }
 async function capture(name){
  await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const pixels=await page.evaluate(()=>{
   const c=document.querySelector('#view'),g=c.getContext('webgl2'),p=new Uint8Array(c.width*c.height*4);
   g.readPixels(0,0,c.width,c.height,g.RGBA,g.UNSIGNED_BYTE,p);
   let count=0,minX=c.width,maxX=0,minY=c.height,maxY=0;
   for(let i=0;i<p.length;i+=4)if(p[i+3]>20){count++;const x=i/4%c.width,y=Math.floor(i/4/c.width);minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}
   return {count,minX,maxX,minY,maxY,w:c.width,h:c.height};
  });
  assert(pixels.count>2000,`Blank ${name}`);
  assert(pixels.minX>0&&pixels.maxX<pixels.w-1&&pixels.minY>0&&pixels.maxY<pixels.h-1,`Clipped ${name}`);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Overflow ${name}`);
  await page.screenshot({path:join(root,name),fullPage:true});checks.push({name,pixels});
 }
 await capture('preview_iso.png');
 for(const view of ['front','rear','inside','side','bottom']){await page.locator(`[data-view="${view}"]`).click();await capture(`preview_${view}.png`);}
 await page.locator('#covers').uncheck();await capture('preview_ports_open.png');
 assert((await page.evaluate(()=>PACKING.inspect())).filter(p=>p.kind==='cover').every(p=>!p.visible));
 await page.locator('[data-view="iso"]').click();
 await page.locator('#reserves').check();await page.locator('#explode').fill('100');await capture('preview_exploded.png');
 await page.setViewportSize({width:390,height:844});await capture('preview_mobile.png');
 await page.locator('[data-part="touch_glass"]').uncheck();
 assert.equal((await page.evaluate(()=>PACKING.inspect())).find(p=>p.id==='touch_glass').visible,false);
 await page.locator('#reset').click();await page.locator('[data-view="inside"]').click();await capture('preview_mobile_inside.png');
 // The old Model 02 entry must serve the selected layout instead of T02.
 await page.goto(pathToFileURL(join(root,'../touchscreen_01/preview.html')).href);
 await page.waitForFunction(()=>window.PACKING?.report?.model==='Model 02 / selected touchscreen layout');
 assert(page.url().endsWith('/touchscreen_02/preview.html'));
 assert.equal(await page.evaluate(()=>PACKING.report.jack_edge),'bottom');
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 await writeFile(join(root,'viewer_validation.json'),JSON.stringify({passed:true,model:report.model,parameter_sha256:report.parameter_sha256,geometry:parts,jack_mouth_mm:report.jack_mouth_mm,legacy_T02_redirect:true,errors,externalRequests:requests,checks},null,2)+'\n');
 console.log('PASS: Model 02 bottom jack, two battery envelopes, unchanged exterior, CAD mesh agreement, desktop/mobile views and legacy redirect');
} finally {await browser.close();}
