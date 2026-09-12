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
 assert(info.validated);assert.equal(info.ids.length,15);assert(!info.ids.some(id=>/wheel|fpc8/.test(id)));
 assert.equal(info.screen.parent,'touch_glass');
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
 for(const view of ['front','back','inside']){await page.locator(`[data-view="${view}"]`).click();await capture(`preview_${view}.png`);}
 await page.locator('[data-view="iso"]').click();
 await page.locator('#explode').fill('65');await capture('preview_exploded.png');
 await page.locator('#reset').click();
 await page.locator('[data-part="battery"]').click();assert((await page.evaluate(()=>T01.getState())).hidden.includes('battery'));
 await page.locator('#reset').click();assert.equal((await page.evaluate(()=>T01.getState())).visible,15);
 await page.setViewportSize({width:390,height:844});await capture('preview_mobile.png');
 await page.locator('[data-view="inside"]').click();await capture('preview_mobile_inside.png');
 await page.setViewportSize({width:1200,height:950});
 await page.goto(pathToFileURL(join(root,'scan/preview.html')).href);
 await page.waitForFunction(()=>window.T01_SCAN);
 assert.equal(await page.evaluate(()=>T01_SCAN.units),'mm');
 assert((await page.evaluate(()=>T01_SCAN.triangles))>1000);
 await page.locator('[data-view="rear"]').click();
 await page.waitForTimeout(400);
 await page.screenshot({path:join(root,'scan/preview_check.png'),fullPage:true});
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 await writeFile(join(root,'viewer_validation.json'),JSON.stringify({passed:true,errors,externalRequests:requests,checks},null,2)+'\n');
 console.log('PASS: desktop/mobile views, exploded assembly, part toggles, no clipping/errors/network requests');
} finally {await browser.close();}
