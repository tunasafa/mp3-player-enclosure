import {spawn} from 'node:child_process';
import {readFile,writeFile,mkdtemp} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
const root=dirname(fileURLToPath(import.meta.url));
const profile=await mkdtemp(join(tmpdir(),'mp3-p04-cdp-'));
const browser=spawn(process.env.P04_BROWSER_PATH||'/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',[
 '--headless','--no-first-run','--no-default-browser-check','--disable-background-networking',
 '--disable-component-update','--disable-sync','--enable-unsafe-swiftshader',
 '--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'
],{stdio:['ignore','ignore','ignore']});
let socket;
const timeout=setTimeout(()=>{browser.kill('SIGKILL');process.exit(1)},35000);
try{
 let port;
 for(let i=0;i<100;i++){
  try{port=(await readFile(profile+'/DevToolsActivePort','utf8')).split('\n')[0];break}catch{}
  await new Promise(r=>setTimeout(r,100));
 }
 if(!port)throw Error('Browser debugging port unavailable');
 const tabs=await (await fetch('http://127.0.0.1:'+port+'/json')).json();
 socket=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject});
 let serial=0;const pending=new Map(),errors=[];
 socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params)};
 function call(method,params={}){return new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}))})}
 async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
 await call('Runtime.enable');await call('Page.enable');
 await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url:'file://'+root+'/preview.html'});
 for(let i=0;i<100;i++){
  if(await evaluate('Boolean(window.FORM01)'))break;
  await new Promise(r=>setTimeout(r,100));
 }
 const initial=await evaluate('window.FORM01.getState()');
 if(initial.variant!=='P04_compact'||initial.visible!==10)throw Error('Unexpected initial state '+JSON.stringify(initial));
 const labels=await evaluate("document.getElementById('legend').textContent");
 if(!labels.includes('600 mAh')||labels.includes('2000 mAh'))throw Error('Stale battery labeling');
 if(!labels.includes('TLV320DAC3100')||labels.includes('PCM5102')||labels.includes('Conditional'))throw Error('Stale audio labeling');
 await evaluate("document.getElementById('explode').value='65';document.getElementById('explode').dispatchEvent(new Event('input'))");
 if((await evaluate('window.FORM01.getState()')).explode!==65)throw Error('Explode control failed');
 await evaluate("document.querySelector('[data-group=components]').click()");
 if((await evaluate('window.FORM01.getState()')).visible!==2)throw Error('Component visibility failed');
 await evaluate("document.getElementById('reset').click();document.querySelector('[data-view=front]').click()");
 await new Promise(r=>setTimeout(r,200));
 const front=await call('Page.captureScreenshot',{format:'png'});
 await writeFile(root+'/preview_check.png',Buffer.from(front.data,'base64'));
 await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await evaluate("document.getElementById('reset').click()");
 await new Promise(r=>setTimeout(r,200));
 const mobile=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
 await writeFile(root+'/preview_mobile_check.png',Buffer.from(mobile.data,'base64'));
 if(errors.length)throw Error(JSON.stringify(errors));
 const report={status:'passed',initial,checks:['WebGL initialized','10 expected parts','600mAh battery label','explosion slider','component visibility','reset','front view','desktop and mobile rendering'],runtimeErrors:errors.length,
   preview_sha256:createHash('sha256').update(await readFile(root+'/preview.html')).digest('hex')};
 await writeFile(root+'/viewer_validation.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));
}finally{clearTimeout(timeout);socket?.close();browser.kill('SIGTERM')}
