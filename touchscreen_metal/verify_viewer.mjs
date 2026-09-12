import assert from 'node:assert/strict';
import { chromium } from '../revision_04/node_modules/playwright/index.mjs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { writeFile } from 'node:fs/promises';
const root=dirname(fileURLToPath(import.meta.url));
const browser=await chromium.launch({executablePath:process.env.T01_BROWSER_PATH||'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',headless:true,args:['--enable-unsafe-swiftshader','--disable-background-networking']});
const errors=[],requests=[],checks=[];
try {
 const page=await browser.newPage({viewport:{width:1440,height:1050}});
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(/^https?:/.test(r.url())) requests.push(r.url());});
 await page.goto(pathToFileURL(join(root,'preview.html')).href);
 await page.waitForFunction(()=>window.T01);
 const info=await page.evaluate(()=>T01.getInspection());
 assert(info.validated);assert.equal(info.ids.length,29);assert(!info.ids.some(id=>/wheel|fpc8/.test(id)));
 assert.equal(info.screen.parent,'touch_glass');
 assert(info.screen.width>info.screen.height,'Screen is not landscape');
 assert.deepEqual(info.validation.collisions,[]);assert.deepEqual(info.validation.reserve_collisions,[]);
 assert.deepEqual(info.validation.outside_case,[]);assert.deepEqual(info.validation.port_wall_obstructions,[]);
 assert.equal(info.validation.display_rear_loading_sweep_intersection_mm3,0);
 assert.equal(info.validation.ports.jack.edge,'bottom');
 assert(Math.abs(info.validation.ports.jack.center[0])<0.001);
 assert(Math.abs(info.validation.ports.jack.center[1]+info.parameters.body.length/2-.4)<.001);
 assert.equal(info.validation.ports.usb.edge,'right');assert.equal(info.validation.ports.microsd.edge,'left');
 assert(info.parameters.battery.center[1]>info.parameters.electronics.find(e=>e.id==='audio').center[1]);
 let uiCount=0;
 for(const part of info.geometry){
  assert.equal(part.physicalMeshes,part.expectedMeshes,`Duplicate physical geometry: ${part.id}`);
  for(let side=0;side<2;side++)for(let axis=0;axis<3;axis++)assert(Math.abs(part.bounds[side][axis]-part.expected[side][axis])<.09,`Viewer/CAD bounds diverge: ${part.id}`);
  uiCount+=part.surfaces.filter(s=>s==='touch-ui').length;
 }
 assert.equal(uiCount,1,'Duplicate touch display surface');
 async function capture(name){
  await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const pixels=await page.evaluate(()=>{
   const c=document.querySelector('#view'),g=c.getContext('webgl2'),p=new Uint8Array(c.width*c.height*4);
   g.readPixels(0,0,c.width,c.height,g.RGBA,g.UNSIGNED_BYTE,p);
   let count=0,minX=c.width,maxX=0,minY=c.height,maxY=0;
   for(let i=0;i<p.length;i+=4) if(p[i+3]>20){count++;const x=i/4%c.width,y=Math.floor(i/4/c.width);minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);}
   return {count,minX,maxX,minY,maxY,w:c.width,h:c.height};
  });
  assert(pixels.count>2000,`Blank ${name}`);
  assert(pixels.minX>0&&pixels.maxX<pixels.w-1&&pixels.minY>0&&pixels.maxY<pixels.h-1,`Clipped ${name}`);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Overflow ${name}`);
  await page.screenshot({path:join(root,name),fullPage:true});checks.push({name,pixels});
 }
 await capture('preview_iso.png');
 for(const view of ['front','back','inside','ports']){await page.locator(`[data-view="${view}"]`).click();await capture(`preview_${view}.png`);}
 await page.locator('[data-view="iso"]').click();
 await page.locator('#explode').fill('65');await capture('preview_exploded.png');
 await page.locator('#explode').fill('100');await capture('preview_exploded_full.png');
 await page.locator('#reset').click();
 await page.locator('[data-part="battery"]').click();assert((await page.evaluate(()=>T01.getState())).hidden.includes('battery'));
 await page.locator('#reset').click();assert.equal((await page.evaluate(()=>T01.getState())).visible,info.ids.length);
 await page.setViewportSize({width:390,height:844});await capture('preview_mobile.png');
 await page.locator('[data-view="inside"]').click();await capture('preview_mobile_inside.png');
 await page.setViewportSize({width:1200,height:950});
 await page.goto(pathToFileURL(join(root,'../touchscreen_01/scan/preview.html')).href);
 await page.waitForFunction(()=>window.T01_SCAN);
 assert.equal(await page.evaluate(()=>T01_SCAN.units),'mm');
 assert((await page.evaluate(()=>T01_SCAN.triangles))>1000);
 await page.locator('[data-view="rear"]').click();
 await page.waitForTimeout(400);
 await page.screenshot({path:join(root,'scan_preview_check.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 await writeFile(join(root,'viewer_validation.json'),JSON.stringify({passed:true,variant:'T03_metal',parameter_sha256:info.validation.parameter_sha256,geometry:info.geometry,ports:info.validation.ports,errors,externalRequests:requests,checks},null,2)+'\n');
 console.log('PASS: desktop/mobile views, exploded assembly, part toggles, no clipping/errors/network requests');
} finally {await browser.close();}
