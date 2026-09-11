import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright';

const root = dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({
  executablePath: process.env.P04_BROWSER_PATH || '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
  headless: true,
  args: ['--enable-unsafe-swiftshader', '--disable-background-networking'],
});
const errors = [], checks = [], captures = [];
try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  const requests = [];
  page.on('request', r => { if (/^https?:/.test(r.url())) requests.push(r.url()); });
  await page.goto(pathToFileURL(join(root, 'preview.html')).href);
  await page.waitForFunction(() => Boolean(window.FORM01));
  const state = () => page.evaluate(() => window.FORM01.getState());
  const inspection = () => page.evaluate(() => window.FORM01.getInspection());
  const settle = () => page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  const pixels = () => page.evaluate(() => {
    const c = document.getElementById('view'), gl = c.getContext('webgl2');
    const rgba = new Uint8Array(c.width * c.height * 4);
    gl.readPixels(0, 0, c.width, c.height, gl.RGBA, gl.UNSIGNED_BYTE, rgba);
    let count = 0, minX = c.width, maxX = 0, minY = c.height, maxY = 0, checksum = 0;
    const colors = new Set();
    for (let i = 0; i < rgba.length; i += 4) {
      if (rgba[i + 3] < 20) continue;
      const x = i / 4 % c.width, y = Math.floor(i / 4 / c.width);
      count++; minX = Math.min(minX, x); maxX = Math.max(maxX, x); minY = Math.min(minY, y); maxY = Math.max(maxY, y);
      checksum = (checksum + (rgba[i] * 3 + rgba[i + 1] * 5 + rgba[i + 2] * 7) * (i % 919 + 1)) % 1000000007;
      colors.add((rgba[i] >> 3) * 1024 + (rgba[i + 1] >> 3) * 32 + (rgba[i + 2] >> 3));
    }
    return { count, colors: colors.size, minX, maxX, minY, maxY, checksum, width: c.width, height: c.height };
  });
  async function capture(name, { fullPage = false } = {}) {
    await settle();
    const p = await pixels();
    assert(p.count > 2000, `${name}: blank canvas`);
    assert(p.colors > 30, `${name}: materials or textures missing`);
    assert(p.minX > 0 && p.maxX < p.width - 1 && p.minY > 0 && p.maxY < p.height - 1, `${name}: model clipped ${JSON.stringify(p)}`);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${name}: horizontal overflow`);
    await page.screenshot({ path: join(root, name), fullPage });
    captures.push({ name, ...p });
  }
  const initial = await state();
  assert.equal(initial.visible, 10);
  assert.equal(initial.variant, 'P04_compact');
  const detail = await inspection();
  assert.equal(detail.screen.parent, 'display_envelope');
  assert(detail.screen.localZ > 1.5 && detail.screen.localZ < 2, 'LCD must be recessed behind lens');
  assert.equal(detail.screen.depthTest, true);
  assert.equal(detail.branding.name, 'mytunas');
  assert.equal(detail.branding.parent, 'rear_shell');
  assert.equal(detail.branding.depth, 0.3);
  assert(Math.abs(detail.branding.bounds.min[2] - 13.1) < 1e-4);
  assert(Math.abs(detail.branding.bounds.max[2] - 13.1) < 1e-4, 'Engraving must be the recessed CAD floor');
  for (const part of detail.parts.filter(p => !['front_bezel', 'rear_shell', 'clear_lens_reference'].includes(p.id))) {
    assert(part.meshes >= 3, `${part.id} remains a single envelope`);
  }
  checks.push('10 parts, multi-material components, recessed depth-tested LCD parented to display');
  await capture('preview_iso_check.png');
  await page.click('[data-view=front]');
  await capture('preview_check.png');
  await page.click('[data-view=back]');
  await capture('preview_rear_check.png');
  await page.click('[data-part=rear_shell]');
  assert.equal((await inspection()).branding.visible, false, 'Rear branding must hide with the cap');
  await page.click('[data-part=rear_shell]');
  assert.equal((await inspection()).branding.visible, true);
  await page.click('[data-view=front]');
  await settle();
  const beforeOrbit = await pixels();
  const bounds = await page.locator('#view').boundingBox();
  await page.mouse.move(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2);
  await page.mouse.down(); await page.mouse.move(bounds.x + bounds.width / 2 + 70, bounds.y + bounds.height / 2 + 20, { steps: 6 }); await page.mouse.up();
  await settle(); assert.notEqual((await pixels()).checksum, beforeOrbit.checksum, 'Orbit did not change rendered pixels');
  checks.push('Pointer orbit changes canvas pixels');
  await page.click('[data-view=inside]');
  assert.equal((await state()).visible, 9);
  assert.equal(await page.locator('[data-group=shell]').isChecked(), false);
  await capture('preview_inside_check.png');
  await page.click('[data-view=front]');
  await page.click('[data-group=shell]');
  await page.click('[data-part=clear_lens_reference]');
  await capture('preview_internal_front_check.png');
  checks.push('Inside preset exposes components; front and rear internal views render');
  await page.click('#reset');
  await page.click('[data-view=front]');
  await page.click('[data-part=clear_lens_reference]');
  await settle();
  assert.equal((await inspection()).screen.visible, true, 'Hiding lens incorrectly hides LCD');
  const withoutLens = await pixels();
  await page.click('[data-part=display_envelope]');
  await settle();
  assert.equal((await inspection()).screen.visible, false, 'Hiding display must hide its UI');
  assert.notEqual((await pixels()).checksum, withoutLens.checksum);
  await page.click('#reset');
  const beforeExplode = await inspection();
  await page.locator('#explode').fill('65');
  await settle();
  assert.equal((await state()).explode, 65);
  const afterExplode = await inspection();
  assert.equal(afterExplode.screen.localZ, beforeExplode.screen.localZ);
  assert.notDeepEqual(afterExplode.screen.world, beforeExplode.screen.world);
  assert.notDeepEqual(afterExplode.branding.world, beforeExplode.branding.world);
  assert.deepEqual(afterExplode.branding.bounds, beforeExplode.branding.bounds);
  assert.equal(afterExplode.parts.find(p => p.id === 'display_envelope').offset, -0.82 * 65 * 0.43);
  await capture('preview_exploded_check.png');
  checks.push('LCD visibility follows display, not lens; LCD moves with display during explosion');
  checks.push('mytunas CAD engraving at Z13.1; lettering/logo follow rear-cap visibility and explosion');
  await page.click('[data-group=components]');
  assert.equal((await state()).visible, 2);
  await page.click('#reset');
  assert.equal((await state()).visible, 10);
  await page.click('#outlines'); await settle();
  await page.click('#zoom-in'); assert((await state()).zoom > 1);
  await page.click('#reset');
  checks.push('Part/layer visibility, outlines, zoom and reset');
  // Every component must survive isolation, including its textured surfaces.
  await page.click('[data-view=back]');
  await page.click('[data-group=shell]');
  await page.click('[data-part=clear_lens_reference]');
  const ids = (await inspection()).parts.filter(p => p.visible).map(p => p.id);
  for (const id of ids) await page.click(`[data-part="${id}"]`);
  assert.equal((await state()).visible, 0);
  for (const id of ids) {
    await page.click(`[data-part="${id}"]`); await settle();
    assert((await pixels()).count > 150, `${id}: missing isolated geometry`);
    await page.click(`[data-part="${id}"]`);
  }
  checks.push('Every internal component renders in isolation');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.click('#reset');
  await capture('preview_mobile_check.png', { fullPage: true });
  await page.click('[data-view=back]');
  await capture('preview_mobile_rear_check.png', { fullPage: true });
  await page.click('[data-view=inside]');
  await capture('preview_mobile_inside_check.png', { fullPage: true });
  await page.click('#reset');
  await page.locator('#explode').fill('100');
  await capture('preview_mobile_exploded_check.png', { fullPage: true });
  await page.setViewportSize({ width: 320, height: 740 });
  await page.click('#reset');
  await capture('preview_small_mobile_check.png', { fullPage: true });
  await page.click('[data-view=back]');
  await capture('preview_small_mobile_rear_check.png', { fullPage: true });
  checks.push('Desktop, 390px mobile and 320px mobile screenshots; nonblank canvas and unclipped geometry');
  assert.deepEqual(requests, [], 'Offline preview made network requests');
  assert.deepEqual(errors, []);
  checks.push('No external requests or runtime errors');
  const report = { status: 'passed', initial, checks, captures, runtimeErrors: errors.length,
    preview_sha256: createHash('sha256').update(await readFile(join(root, 'preview.html'))).digest('hex') };
  await writeFile(join(root, 'viewer_validation.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
