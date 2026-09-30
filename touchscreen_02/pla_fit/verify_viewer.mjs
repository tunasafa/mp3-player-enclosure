import assert from 'node:assert/strict';
import { chromium } from '../../revision_04/node_modules/playwright/index.mjs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const root=dirname(fileURLToPath(import.meta.url));
const expected=JSON.parse(await readFile(join(root,'validation.json'),'utf8'));
const sha=async p=>createHash('sha256').update(await readFile(p)).digest('hex');
for(const [p,h] of Object.entries(expected.source_sha256))assert.equal(await sha(join(root,'../..',p)),h);
assert(expected.passed);
const browser=await chromium.launch({executablePath:'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',headless:true,args:['--enable-unsafe-swiftshader','--disable-background-networking']});
const errors=[],requests=[],captures=[];
try {
 const page=await browser.newPage({viewport:{width:1280,height:1000}});
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
 await page.goto(pathToFileURL(join(root,'preview.html')).href);
 await page.waitForFunction(()=>window.PACKING);
 assert.deepEqual(await page.evaluate(()=>PACKING.report),expected);
 const parts=await page.evaluate(()=>PACKING.inspect());
 assert.equal(parts.filter(p=>p.kind==='structure').length,4);
 assert.equal(parts.filter(p=>p.kind==='fastener').length,0);
 for(const p of parts){
  assert.equal(p.physicalMeshes,p.expectedMeshes);
  for(let side=0;side<2;side++)for(let axis=0;axis<3;axis++)assert(Math.abs(p.bounds[side][axis]-p.expected[side][axis])<.09,p.id+' mesh/CAD mismatch');
 }
 async function capture(name){
  await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const pixels=await page.evaluate(()=>{
   const c=document.querySelector('#view'),gl=c.getContext('webgl2'),p=new Uint8Array(c.width*c.height*4);
   gl.readPixels(0,0,c.width,c.height,gl.RGBA,gl.UNSIGNED_BYTE,p);
   let count=0;for(let i=3;i<p.length;i+=4)if(p[i]>20)count++;
   return count;
  });
  assert(pixels>2000,'Blank render '+name);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:join(root,'preview_'+name+'.png'),fullPage:true});
  captures.push({name,pixels});
 }
 await capture('iso');
 await page.locator('[data-view="inside"]').click();
 assert.equal((await page.evaluate(()=>PACKING.inspect())).find(p=>p.id==='rear_lid').visible,false);
 await capture('inside');
 // Structural-only inside view makes the new rails and shelves reviewable.
 for(const p of parts)if(p.kind!=='structure'&&p.kind!=='reserve')await page.locator(`[data-part="${p.id}"]`).uncheck();
 await capture('supports');
 await page.locator('#reset').click();
 await page.locator('#explode').fill('55');
 await page.locator('[data-view="iso"]').click();
 await capture('exploded');
 await page.locator('#reset').click();
 await page.locator('[data-view="rear"]').click();
 await capture('rear');
 await page.locator('[data-view="latch"]').click();
 await capture('latch');
 await page.setViewportSize({width:390,height:844});
 await page.locator('#reset').click();
 await capture('mobile');
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 await writeFile(join(root,'viewer_validation.json'),JSON.stringify({passed:true,source_sha256:expected.source_sha256,captures,errors,external_requests:requests},null,2)+'\n');
 console.log('PASS: CAD/mesh bounds, four printed parts, no fasteners, offline desktop/mobile and seven screenshots.');
} finally {await browser.close();}
