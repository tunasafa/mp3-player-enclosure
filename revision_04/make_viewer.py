#!/usr/bin/env python3
"""Rebuild the standalone offline viewer from assembly-coordinate reference STLs.

Run from this folder with: .venv/bin/python make_viewer.py
No server, CDN or browser-side package is required to open preview.html.
"""
from pathlib import Path
import base64
import hashlib
import json

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
PARAMETERS = json.loads((ROOT / "parameters.json").read_text())
PARTS = {
    "front_bezel": ("Front bezel", "shell", "#e9e5db", -1.20, 0),
    "rear_shell": ("Rear shell", "shell", "#bfc8c6", 1.55, 0),
    "clear_lens_reference": ("Lens / screen face", "components", "#1d3941", -1.20, 3),
    "display_envelope": ("ST7789 display", "components", "#344c54", -0.82, 1),
    "clickwheel_envelope": ("Clickwheel assembly", "components", "#d9ded9", -0.82, 2),
    "battery_envelope": ("503040 battery · 600 mAh", "components", "#d8af55", 0.45, 0),
    "xiao": ("XIAO ESP32-S3", "components", "#688e7e", 0.76, 0),
    "dac": ("TLV320DAC3100 · earphone output", "components", "#998fae", 0.76, 0),
    "microsd": ("microSD module", "components", "#6e99ab", 0.76, 0),
    "fpc8": ("Clickwheel adapter · 2.85 mm wall gap", "components", "#7f9c91", 0.76, 0),
}


def pack(array):
    return base64.b64encode(np.asarray(array, dtype="<f4").tobytes()).decode("ascii")


geometries = {}
variants = {}
for variant in ("P04_compact",):
    parts = []
    for name, (label, group, color, explode, kind) in PARTS.items():
        path = ROOT / "designs" / variant / "reference_only" / f"{name}.stl"
        mesh = trimesh.load(path, force="mesh", process=True)
        vertices = mesh.vertices[mesh.faces].reshape((-1, 3))
        normals = np.repeat(mesh.face_normals, 3, axis=0)
        buffer = np.hstack((vertices, normals)).astype("<f4")
        signature = hashlib.sha256(buffer.tobytes()).hexdigest()[:20]
        if signature not in geometries:
            sharp = mesh.face_adjacency_edges[mesh.face_adjacency_angles > 0.55]
            unique_edges, counts = np.unique(np.sort(mesh.edges, axis=1), axis=0, return_counts=True)
            boundary = unique_edges[counts == 1]
            edges = np.vstack((sharp, boundary)) if len(boundary) else sharp
            edge_positions = mesh.vertices[edges].reshape((-1, 3))
            edge_buffer = np.hstack((edge_positions, np.zeros_like(edge_positions)))
            geometries[signature] = {"triangles": pack(buffer), "lines": pack(edge_buffer)}
        parts.append({"id": name, "label": label, "group": group, "color": color,
                      "explode": explode, "kind": kind, "geometry": signature})
    variants[variant] = parts

DATA = json.dumps({"geometries": geometries, "variants": variants,
                   "body": PARAMETERS["body"]}, separators=(",", ":"))

HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FORM 04 — MP3 player / fit study</title>
<style>
:root{--paper:#f4f2eb;--ink:#253b40;--muted:#74817d;--line:#d9ddd4;--accent:#8b643d;--green:#486c60;--panel:#faf9f4}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:Arial,Helvetica,sans-serif;-webkit-font-smoothing:antialiased}button,input{font:inherit}button{cursor:pointer;color:inherit}button:focus-visible,input:focus-visible,canvas:focus-visible{outline:2px solid var(--green);outline-offset:4px}.page{max-width:1600px;margin:0 auto;padding:30px 40px 20px}.masthead{display:flex;align-items:center;justify-content:space-between;padding-bottom:24px;border-bottom:1px solid var(--line);gap:20px}.wordmark{font-size:13px;font-weight:700;letter-spacing:.16em}.wordmark span{font-weight:400;color:var(--muted);margin-left:13px}.revision{font:11px monospace;color:var(--muted);letter-spacing:.06em}.layout{display:grid;grid-template-columns:minmax(0,1fr) 305px;min-height:700px}.stage{position:relative;min-width:0;min-height:680px;overflow:hidden;background:radial-gradient(ellipse at 48% 48%,#fffefa 0,#f1f0e8 62%,#eceee7 100%);border-right:1px solid var(--line)}.stage::before{content:"";position:absolute;inset:0;background-image:radial-gradient(#84948d33 .8px,transparent .8px);background-size:22px 22px;pointer-events:none}.stage-top{position:absolute;top:27px;left:28px;right:28px;display:flex;justify-content:space-between;z-index:2;gap:16px;pointer-events:none}.eyebrow{font:10px monospace;letter-spacing:.14em;color:var(--muted);text-transform:uppercase}.viewname{font-size:22px;font-weight:400;letter-spacing:-.025em;margin-top:7px}.badge{height:max-content;white-space:nowrap;padding:7px 9px;border:1px solid #bbbea9;background:#f8f5e8;color:#81704d;font:10px monospace}.viewport{display:block;width:100%;height:680px;position:relative;touch-action:none;cursor:grab}.viewport.dragging{cursor:grabbing}.stage-bottom{position:absolute;bottom:25px;left:28px;right:28px;display:flex;align-items:flex-end;justify-content:space-between;pointer-events:none;gap:15px}.dimension{font-size:12px;letter-spacing:.12em}.dimension small{display:block;font-size:10px;margin-top:8px;color:var(--muted);letter-spacing:.03em}.orbit-hint{font:10px monospace;color:var(--muted);line-height:1.8;text-align:right}.axis{position:absolute;left:28px;bottom:100px;width:75px;height:75px;pointer-events:none}.view-buttons{position:absolute;right:26px;bottom:93px;display:flex;gap:5px}.tiny{border:1px solid #d4d9d0;border-radius:3px;padding:8px 10px;background:#f9faf5;font:10px monospace}.tiny:hover{background:#e7ece4}.side{padding:28px 25px;background:var(--panel)}.intro{font-size:25px;line-height:1.17;letter-spacing:-.04em;font-weight:400;margin:8px 0 12px}.description{font-size:12px;line-height:1.7;color:#6b7a76;margin:0 0 23px}.section{border-top:1px solid var(--line);padding-top:20px;margin-top:22px}.label{display:flex;align-items:center;justify-content:space-between;font:10px monospace;letter-spacing:.07em;color:var(--muted);margin-bottom:12px}.variant{width:100%;text-align:left;background:#f5f5ee;border:1px solid #d7dcd2;padding:12px 13px;margin-bottom:8px;border-radius:3px;display:grid;grid-template-columns:23px 1fr 12px;gap:7px;align-items:center}.variant b{font:12px monospace;color:#809187}.variant strong{display:block;font-size:12px;font-weight:500}.variant small{font-size:10px;display:block;color:var(--muted);margin-top:4px}.variant.active{border-color:var(--green);background:#eaf0e7}.variant.active b{color:var(--green)}.variant i{border:1px solid #b5c1b6;width:10px;height:10px;border-radius:100%;display:block}.variant.active i{background:var(--green);border-color:var(--green);box-shadow:0 0 0 3px #f7f9f2 inset}.range{width:100%;accent-color:var(--green);margin:5px 0 2px;cursor:pointer}.range-labels{display:flex;justify-content:space-between;color:#8c9690;font:9px monospace;margin-top:4px}.checks{display:grid;gap:10px;font-size:11px}.check{display:flex;align-items:center;justify-content:space-between;cursor:pointer}.check input{accent-color:var(--green);width:14px;height:14px;margin:0}.legend{display:grid;gap:7px;max-height:164px;overflow:auto;padding-right:6px}.legend-row{display:flex;align-items:center;gap:8px;font-size:10px;line-height:1.3;cursor:pointer}.swatch{width:8px;height:8px;border-radius:2px;flex:none;border:1px solid #00000013}.legend-row.off{opacity:.35}.legend-hint{font-size:9px;color:#8a958e;margin:9px 0 0;line-height:1.5}.footer{display:flex;justify-content:space-between;align-items:flex-start;gap:35px;border-top:1px solid var(--line);padding-top:18px;color:#7b8680;font-size:10px;line-height:1.65}.footer p{margin:0;max-width:720px}.footer a{color:var(--green);text-underline-offset:3px}.footer .offline{white-space:nowrap;font:10px monospace;margin-top:4px}.error{position:absolute;left:10%;right:10%;top:40%;padding:24px;background:var(--panel);border:1px solid var(--line);line-height:1.7;display:none}.count{position:absolute;top:100px;left:28px;font:9px monospace;color:#8e9c94;pointer-events:none}.no-select{user-select:none}
@media(min-width:1200px){.viewport{height:740px}.stage{min-height:740px}.side{padding:30px}}
@media(max-width:860px){.page{padding:18px}.layout{grid-template-columns:1fr}.stage{border-right:0;border-bottom:1px solid var(--line);min-height:550px}.viewport{height:550px}.side{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:24px}.side .section{margin-top:0}.intro-block{grid-column:1/-1}.intro{font-size:23px;margin-bottom:6px}.description{margin-bottom:0}.masthead{padding-bottom:18px}.revision{display:none}.badge{font-size:8px}.stage-top{left:18px;right:18px}.stage-bottom{left:18px;right:18px}.footer{padding-top:15px}.offline{display:none}}
@media(max-width:480px){.page{padding:12px}.wordmark{font-size:11px}.wordmark span{margin-left:7px}.viewport{height:540px}.stage{min-height:540px}.viewname{font-size:19px}.stage-top{flex-wrap:wrap}.badge{position:absolute;top:52px;left:0}.count{display:none}.side{padding:22px 12px;gap:22px 16px}.dimension{font-size:10px}.orbit-hint{font-size:8px}.view-buttons{bottom:85px;right:15px}.axis{left:16px;bottom:87px}.footer{font-size:9px}.legend{max-height:195px}}
</style>
</head>
<body><div class="page">
<header class="masthead"><div class="wordmark">FORM 04 <span>/ MP3 PLAYER</span></div><div class="revision">P04 &nbsp; / &nbsp; MECHANICAL FIT STUDY &nbsp; / &nbsp; 2026</div></header>
<main class="layout">
<section class="stage no-select" aria-label="Interactive enclosure model">
<canvas id="view" class="viewport" tabindex="0" aria-label="3D model. Drag to orbit, scroll to zoom. Arrow keys rotate. Plus and minus zoom. Home resets."></canvas>
<div class="stage-top"><div><div class="eyebrow">Assembly / scale in millimetres</div><div id="viewname" class="viewname">P04 — Compact construction</div></div><div class="badge">Fit prototype · dimensions unverified</div></div>
<div class="count" id="meshcount"></div><canvas id="axis" class="axis" width="150" height="150" aria-hidden="true"></canvas>
<div class="view-buttons"><button class="tiny" data-view="front">Front</button><button class="tiny" data-view="back">Rear</button><button class="tiny" data-view="iso">3D</button><button class="tiny" id="reset">Reset</button></div>
<div class="stage-bottom"><div class="dimension">134 × 72 × 13.4 <small>Length × width × thickness / mm</small></div><div class="orbit-hint">DRAG TO ORBIT<br>SCROLL TO ZOOM</div></div>
<div class="error" id="error">This viewer needs WebGL. Open this HTML file in a browser with hardware acceleration enabled. The manufacturing files are available separately in the designs folder.</div>
</section>
<aside class="side">
<div class="intro-block"><div class="eyebrow">Landscape display / revised internals</div><h1 class="intro">Earphones plug<br>straight in.</h1><p class="description">An integrated DAC and headphone amplifier, a top earphone socket, and the 600 mAh battery. The case gains 0.9 mm in thickness to fit the selected board.</p></div>
<div><div class="label">01 / CONSTRUCTION</div>
<button class="variant active" data-variant="P04_compact" aria-pressed="true"><b>04</b><span><strong>Compact / all printed</strong><small>Local supports · no middle plate</small></span><i></i></button></div>
<div class="section"><label class="label" for="explode"><span>02 / EXPLODED ASSEMBLY</span><output id="explode-out">0%</output></label><input id="explode" class="range" type="range" min="0" max="100" value="0"><div class="range-labels"><span>ASSEMBLED</span><span>SEPARATED</span></div></div>
<div class="section"><div class="label">03 / VISIBLE LAYERS</div><div class="checks"><label class="check">Printed shells<input type="checkbox" data-group="shell" checked></label><label class="check">Component envelopes<input type="checkbox" data-group="components" checked></label><label class="check">Technical outlines<input id="outlines" type="checkbox" checked></label></div></div>
<div class="section"><div class="label">04 / PARTS IN THIS STUDY</div><div class="legend" id="legend"></div><p class="legend-hint">Click a part to hide or show it. Coloured components represent assumed fit envelopes.</p></div>
</aside></main>
<footer class="footer"><p>Actual assembly-coordinate STL geometry. Component dimensions, ports, mounting and flex routes need physical verification. Exploded offsets explain the layout; they are not an assembly sequence. Screen and centre-button surface marks are illustrative. <a href="README.md">Assembly &amp; assumptions</a></p><div class="offline">EMBEDDED GEOMETRY / FULLY OFFLINE</div></footer>
</div>
<script id="model-data" type="application/json">__DATA__</script>
<script>
(()=>{'use strict';
const data=JSON.parse(document.getElementById('model-data').textContent),canvas=document.getElementById('view'),gl=canvas.getContext('webgl',{antialias:true,alpha:true,preserveDrawingBuffer:true});
if(!gl){document.getElementById('error').style.display='block';return;}
const vertex=`attribute vec3 aPos;attribute vec3 aNormal;uniform vec2 uAngles;uniform vec2 uScale;uniform float uOffset;varying vec3 vNormal;varying vec3 vPos;
vec3 rot(vec3 p){float cy=cos(uAngles.x),sy=sin(uAngles.x),cx=cos(uAngles.y),sx=sin(uAngles.y);p=vec3(cy*p.x+sy*p.z,p.y,-sy*p.x+cy*p.z);return vec3(p.x,cx*p.y-sx*p.z,sx*p.y+cx*p.z);}
void main(){vPos=aPos;vec3 p=rot(vec3(aPos.x,aPos.y,6.7-aPos.z-uOffset));vNormal=rot(vec3(aNormal.x,aNormal.y,-aNormal.z));gl_Position=vec4(p.xy*uScale,-p.z/500.0,1.0);}`;
const fragment=`precision mediump float;uniform vec3 uColor;uniform float uKind;uniform float uLine;varying vec3 vNormal;varying vec3 vPos;
void main(){vec3 c=uColor;if(uLine>0.5){gl_FragColor=vec4(c,1.0);return;}
if(uKind>1.5&&uKind<2.5&&vPos.z<0.35){vec2 w=vPos.xy-vec2(0.0,-15.0);float r=length(w);if(r<6.7)c=vec3(.67,.73,.70);if(abs(r-7.0)<.16)c=vec3(.52,.61,.57);if(r>7.6&&r<20.5){float a=atan(w.y,w.x);if(abs(a)<.06||abs(abs(a)-1.5708)<.06||abs(abs(a)-3.1416)<.06)c=vec3(.72,.78,.75);}if(r<5.2&&r>4.8)c=vec3(.60,.68,.65);}
if(uKind>2.5&&vPos.z<0.2){c=vec3(.055,.12,.14);vec2 q=vPos.xy-vec2(0.,38.);float hw=20.0,hh=15.0;if(abs(q.x)<hw&&abs(q.y)<hh){c=vec3(.06,.13,.15);if(q.y>12.5&&q.y<14.0){c=vec3(.08,.16,.18);if(q.x>-19.&&q.x<-15.&&abs(q.y-13.25)<.5)c=vec3(.35,.55,.50);if(q.x>-14.&&q.x<-10.&&abs(q.y-13.25)<.5)c=vec3(.30,.48,.44);if(q.x>15.&&q.x<17.5){float bx=(q.x-15.)/(17.5-15.);if(abs(q.y-13.25)<.5)c=vec3(.35,.55,.50);if(bx>.7&&abs(q.y-13.6)<.25)c=vec3(.06,.13,.15);if(bx>.15&&bx<.25&&abs(q.y-13.25)<.35)c=vec3(.06,.13,.15);}if(q.x>12.5&&q.x<14.5&&abs(q.y-13.25)<.5)c=vec3(.28,.45,.42);}if(q.x>-19.&&q.x<-7.&&q.y>-3.&&q.y<11.5){c=vec3(.12,.22,.24);float ax=q.x+13.,ay=q.y-4.25;if(abs(ax)<5.5&&abs(ay)<6.5)c=vec3(.15,.28,.30);if(abs(ax)<4.5&&abs(ay)<5.5){float t=ax*.3+ay*.5;c=mix(vec3(.10,.25,.30),vec3(.18,.35,.28),smoothstep(-4.,4.,t));}if(abs(ax)<2.5&&abs(ay)<2.5){float cr=length(vec2(ax,ay));if(cr<2.2)c=vec3(.22,.38,.34);if(cr<1.5)c=mix(vec3(.20,.35,.32),vec3(.30,.48,.40),smoothstep(0.,1.5,cr));if(cr<.5)c=vec3(.15,.28,.26);}}if(q.x>-5.&&q.x<19.&&q.y>7.&&q.y<11.){if(q.x>-4.5&&q.x<12.&&abs(q.y-9.8)<.7)c=vec3(.45,.65,.58);if(q.x>-4.5&&q.x<7.&&abs(q.y-7.9)<.55)c=vec3(.28,.45,.42);}if(q.x>-5.&&q.x<19.&&q.y>1.5&&q.y<5.5){if(q.x>-4.5&&q.x<14.&&abs(q.y-4.5)<.5)c=vec3(.35,.55,.50);if(q.x>-4.5&&q.x<8.&&abs(q.y-3.0)<.45)c=vec3(.25,.42,.38);}if(abs(q.y+6.)<.15&&q.x>-18.&&q.x<18.){c=vec3(.10,.20,.22);float prog=smoothstep(-18.,18.,q.x);if(q.x<-18.+36.*.38)c=vec3(.35,.55,.50);float dp=q.x-(-18.+36.*.38);if(abs(dp)<.6)c=vec3(.50,.72,.62);}if(q.y<-7.5&&q.y>-13.){float cy2=q.y+10.5;if(abs(q.x)<2.0){float tx=q.x+1.2;if(tx>-.2&&tx<2.2&&abs(cy2)<1.8){float tri=1.8-abs(cy2);if(tx<tri*.7)c=vec3(.45,.65,.58);}}if(q.x>5.5&&q.x<9.5){float sx=(q.x-6.5);if(abs(cy2)<1.3){float tri=1.3-abs(cy2);if(sx<tri*.65)c=vec3(.35,.55,.50);}if(abs(cy2)<1.3){float tri=1.3-abs(cy2);float sx2=q.x-8.0;if(sx2>0.&&sx2<tri*.65)c=vec3(.35,.55,.50);}}if(q.x>-9.5&&q.x<-5.5){float sx3=-q.x-6.5;if(abs(cy2)<1.3){float tri=1.3-abs(cy2);if(sx3<tri*.65)c=vec3(.35,.55,.50);}if(abs(cy2)<1.3){float tri=1.3-abs(cy2);float sx4=-q.x-8.0;if(sx4>0.&&sx4<tri*.65)c=vec3(.35,.55,.50);}}}if(abs(q.x-hw)<.3&&abs(q.y)<hh)c=vec3(.04,.09,.11);if(abs(q.x+hw)<.3&&abs(q.y)<hh)c=vec3(.04,.09,.11);if(abs(q.y-hh)<.3&&abs(q.x)<hw)c=vec3(.04,.09,.11);if(abs(q.y+hh)<.3&&abs(q.x)<hw)c=vec3(.04,.09,.11);}}
vec3 n=normalize(vNormal);if(!gl_FrontFacing)n=-n;float light=.67+.25*max(dot(n,normalize(vec3(-.4,.7,1.))),0.)+.08*abs(n.z);gl_FragColor=vec4(c*light,1.0);}`;
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
const loc={};['aPos','aNormal'].forEach(n=>loc[n]=gl.getAttribLocation(program,n));['uAngles','uScale','uOffset','uColor','uKind','uLine'].forEach(n=>loc[n]=gl.getUniformLocation(program,n));
function decode(s){const b=atob(s),a=new Uint8Array(b.length);for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return new Float32Array(a.buffer);}
function upload(encoded){const values=decode(encoded),b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,values,gl.STATIC_DRAW);return{buffer:b,count:values.length/6};}
const meshes={};Object.entries(data.geometries).forEach(([key,g])=>meshes[key]={triangles:upload(g.triangles),lines:upload(g.lines)});
let variant='P04_compact',yaw=-.50,pitch=-.14,zoom=1,explode=0,outline=true,dirty=true;const groups={shell:true,carrier:true,components:true},hidden=new Set();
function rgb(hex){return[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255);}
function bind(b){gl.bindBuffer(gl.ARRAY_BUFFER,b.buffer);gl.enableVertexAttribArray(loc.aPos);gl.enableVertexAttribArray(loc.aNormal);gl.vertexAttribPointer(loc.aPos,3,gl.FLOAT,false,24,0);gl.vertexAttribPointer(loc.aNormal,3,gl.FLOAT,false,24,12);}
gl.enable(gl.DEPTH_TEST);gl.depthFunc(gl.LEQUAL);gl.disable(gl.CULL_FACE);gl.frontFace(gl.CW);gl.clearColor(0,0,0,0);
function rotation(x,y,z){let cy=Math.cos(yaw),sy=Math.sin(yaw),cx=Math.cos(pitch),sx=Math.sin(pitch),xx=cy*x+sy*z,zz=-sy*x+cy*z;return[xx,cx*y-sx*zz,sx*y+cx*zz];}
function axes(){const c=document.getElementById('axis'),ctx=c.getContext('2d');ctx.clearRect(0,0,150,150);ctx.lineWidth=2;ctx.font='16px monospace';const vs=[[1,0,0,'X','#a17e60'],[0,1,0,'Y','#728a77'],[0,0,-1,'Z','#8098a3']];vs.sort((a,b)=>rotation(...a.slice(0,3))[2]-rotation(...b.slice(0,3))[2]);for(const v of vs){const r=rotation(...v.slice(0,3));ctx.strokeStyle=v[4];ctx.fillStyle=v[4];ctx.beginPath();ctx.moveTo(67,81);ctx.lineTo(67+r[0]*39,81-r[1]*39);ctx.stroke();ctx.fillText(v[3],62+r[0]*55,86-r[1]*55);}ctx.fillStyle='#94a294';ctx.beginPath();ctx.arc(67,81,3,0,7);ctx.fill();}
function render(){if(!dirty)return;dirty=false;const ratio=Math.min(window.devicePixelRatio||1,2),w=Math.round(canvas.clientWidth*ratio),h=Math.round(canvas.clientHeight*ratio);if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}gl.viewport(0,0,w,h);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);const aspect=w/h,span=(canvas.clientWidth<480?225:195)/zoom;gl.uniform2f(loc.uScale,2/(span*aspect),2/span);gl.uniform2f(loc.uAngles,yaw,pitch);const visible=data.variants[variant].filter(p=>groups[p.group]&&!hidden.has(p.id));gl.enable(gl.POLYGON_OFFSET_FILL);gl.polygonOffset(1,1);gl.uniform1f(loc.uLine,0);let faces=0;
for(const p of visible){const m=meshes[p.geometry];gl.uniform1f(loc.uOffset,explode*.43*p.explode);gl.uniform3fv(loc.uColor,rgb(p.color));gl.uniform1f(loc.uKind,p.kind);bind(m.triangles);gl.drawArrays(gl.TRIANGLES,0,m.triangles.count);faces+=m.triangles.count/3;}
gl.disable(gl.POLYGON_OFFSET_FILL);if(outline){gl.uniform1f(loc.uLine,1);for(const p of visible){const m=meshes[p.geometry];gl.uniform1f(loc.uOffset,explode*.43*p.explode);gl.uniform3fv(loc.uColor,rgb(p.color).map(c=>c*.62));bind(m.lines);gl.drawArrays(gl.LINES,0,m.lines.count);}}
document.getElementById('meshcount').textContent=visible.length+' VISIBLE PARTS  /  '+faces.toLocaleString()+' TRIANGLES';axes();}
function invalidate(){dirty=true;requestAnimationFrame(render);}
function legend(){const el=document.getElementById('legend');el.textContent='';data.variants[variant].forEach(p=>{const row=document.createElement('div');row.className='legend-row'+(hidden.has(p.id)?' off':'');row.tabIndex=0;row.setAttribute('role','button');row.setAttribute('aria-pressed',String(!hidden.has(p.id)));const s=document.createElement('span');s.className='swatch';s.style.background=p.color;row.appendChild(s);row.appendChild(document.createTextNode(p.label));function toggle(){hidden.has(p.id)?hidden.delete(p.id):hidden.add(p.id);legend();invalidate();}row.onclick=toggle;row.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle();}};el.appendChild(row);});}
document.querySelectorAll('[data-variant]').forEach(b=>b.onclick=()=>{variant=b.dataset.variant;document.querySelectorAll('[data-variant]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});document.getElementById('viewname').textContent='P04 — Compact construction';legend();invalidate();});
document.getElementById('explode').oninput=e=>{const old=explode;explode=Number(e.target.value);document.getElementById('explode-out').textContent=explode+'%';if(old===0&&explode>0&&Math.abs(yaw)<.2)yaw=-.65;invalidate();};
document.querySelectorAll('[data-group]').forEach(c=>c.onchange=()=>{groups[c.dataset.group]=c.checked;invalidate();});document.getElementById('outlines').onchange=e=>{outline=e.target.checked;invalidate();};
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{if(b.dataset.view==='front'){yaw=0;pitch=0;}else if(b.dataset.view==='back'){yaw=Math.PI;pitch=0;}else{yaw=-.5;pitch=-.14;}invalidate();});
document.getElementById('reset').onclick=()=>{yaw=-.5;pitch=-.14;zoom=1;explode=0;hidden.clear();Object.keys(groups).forEach(g=>groups[g]=true);document.querySelectorAll('[data-group]').forEach(c=>c.checked=true);document.getElementById('explode').value=0;document.getElementById('explode-out').textContent='0%';outline=true;document.getElementById('outlines').checked=true;legend();invalidate();};
let drag=null;canvas.onpointerdown=e=>{drag={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);canvas.classList.add('dragging');};canvas.onpointermove=e=>{if(!drag)return;yaw+=(e.clientX-drag.x)*.009;pitch=Math.max(-1.48,Math.min(1.48,pitch+(e.clientY-drag.y)*.009));drag={x:e.clientX,y:e.clientY};invalidate();};function end(){drag=null;canvas.classList.remove('dragging');}canvas.onpointerup=end;canvas.onpointercancel=end;canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.50,Math.min(2.5,zoom*Math.exp(-e.deltaY*.001)));invalidate();},{passive:false});canvas.onkeydown=e=>{if(e.key==='ArrowLeft')yaw-=.12;else if(e.key==='ArrowRight')yaw+=.12;else if(e.key==='ArrowUp')pitch=Math.max(-1.48,pitch-.12);else if(e.key==='ArrowDown')pitch=Math.min(1.48,pitch+.12);else if(e.key==='+'||e.key==='=')zoom=Math.min(2.5,zoom*1.1);else if(e.key==='-')zoom=Math.max(.5,zoom/1.1);else if(e.key==='Home'){document.getElementById('reset').click();}else return;e.preventDefault();invalidate();};
new ResizeObserver(invalidate).observe(canvas);window.addEventListener('resize',invalidate);legend();invalidate();window.FORM01={getState:()=>({variant,yaw,pitch,zoom,explode,groups:{...groups},visible:data.variants[variant].filter(p=>groups[p.group]&&!hidden.has(p.id)).length}),render:invalidate};
})();
</script></body></html>'''

output = ROOT / "preview.html"
output.write_text(HTML.replace("__DATA__", DATA))
print(f"Wrote {output.name}: {output.stat().st_size:,} bytes, {len(geometries)} unique meshes")
