import {Quaternion, Vector3} from 'three';

// Shared presentation for the metal and PLA viewers; bundled into each offline HTML.
export function setupViewerUI(camera, groups, checks) {
  const slider = document.querySelector('#explode');
  const output = document.querySelector('#explode-out');
  const count = document.querySelector('#meshcount');
  const heading = document.querySelector('#viewname');
  const initialHeading = heading.textContent;
  const titles = {front: 'Front elevation', rear: 'Rear elevation', inside: 'Inside / service access',
    side: 'Side elevation', bottom: 'Bottom / headphone jack', usb: 'USB-C / right edge',
    sd: 'microSD / left edge', jack: 'Headphones / bottom edge', latch: 'Top release tongue'};

  for (const [id, check] of checks) {
    const group = groups.get(id), label = check.parentElement;
    const swatch = document.createElement('span');
    swatch.className = 'swatch';
    swatch.setAttribute('aria-hidden', 'true');
    swatch.style.backgroundColor = '#' + group.children[0].material.color.getHexString();
    const name = document.createElement('span');
    name.className = 'part-name';
    name.textContent = group.userData.label.split(' / ')[0];
    check.setAttribute('aria-label', group.userData.label);
    label.title = group.userData.label + '\n' + label.title;
    label.replaceChildren(swatch, name, check);
  }

  function update() {
    output.value = slider.value + '%';
    let visible = 0, triangles = 0;
    for (const [id, group] of groups) {
      if (checks.has(id)) checks.get(id).parentElement.classList.toggle('off', !group.visible);
      if (!group.visible || group.userData.reserve) continue;
      visible++;
      for (const mesh of group.children) triangles += (mesh.geometry.index?.count ?? mesh.geometry.attributes.position.count) / 3;
    }
    count.textContent = `${visible} VISIBLE PARTS / ${Math.round(triangles).toLocaleString()} TRIANGLES`;
    const selected = document.querySelector('[data-view][aria-pressed="true"]')?.dataset.view;
    heading.textContent = titles[selected] ? `Model 02 — ${titles[selected]}` : initialHeading;
  }
  // Run after the existing assembly handlers, including presets and Reset.
  for (const event of ['input', 'change', 'click']) {
    document.querySelector('main').addEventListener(event, () => requestAnimationFrame(update));
  }
  update();

  const canvas = document.querySelector('#axis'), ctx = canvas.getContext('2d');
  const previous = new Quaternion(0, 0, 0, 0), inverse = new Quaternion();
  const axes = [[1, 0, 0, 'X', '#a17e60'], [0, 1, 0, 'Y', '#728a77'], [0, 0, 1, 'Z', '#8098a3']];
  return function drawAxes() {
    if (previous.equals(camera.quaternion)) return;
    previous.copy(camera.quaternion);
    inverse.copy(camera.quaternion).invert();
    const projected = axes.map(([x, y, z, name, color]) => ({v: new Vector3(x, y, z).applyQuaternion(inverse), name, color}));
    projected.sort((a, b) => a.v.z - b.v.z);
    ctx.clearRect(0, 0, 150, 150);
    ctx.lineWidth = 2;
    ctx.font = '16px monospace';
    for (const {v, name, color} of projected) {
      ctx.strokeStyle = ctx.fillStyle = color;
      ctx.beginPath(); ctx.moveTo(67, 81); ctx.lineTo(67 + v.x * 39, 81 - v.y * 39); ctx.stroke();
      ctx.fillText(name, 62 + v.x * 55, 86 - v.y * 55);
    }
    ctx.fillStyle = '#94a294'; ctx.beginPath(); ctx.arc(67, 81, 3, 0, Math.PI * 2); ctx.fill();
  };
}
