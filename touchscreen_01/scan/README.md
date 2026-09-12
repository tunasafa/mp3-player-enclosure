# Display scan inspection

Source: user-uploaded `Scaniverse_2026_09_12_145606.obj` in
`revision_04/designs/P04_compact/reference_only/`. The original is unchanged.
Open the [inspection image](inspection.png), [interactive scan](preview.html),
[raw context image](raw_inspection.png) or [numeric report](scan_report.json).

The OBJ explicitly declares **metres**, so coordinates were multiplied by 1000
to inspect in millimetres. It contains 60,440 vertices and 115,278 triangles,
including a large support surface. The whole scan's approximately 235 × 193 mm
horizontal bounding box is therefore **not the display size**.

The analysis fits a plane to distant support-surface points, removes its small
tilt, approximately aligns the panel in plan by 31.5 degrees and crops a region
containing the body and folded ribbons. The 95th percentile residual on selected
support samples is about **0.54 mm**; this is observed surface variation, not a
certified uncertainty bound or calibration of the display dimensions.

With different height thresholds, the selected body region's 1st-to-99th-percentile
extent ranges roughly **34–37 mm across and 43.5–44.6 mm along**. The lower-height
thresholds include more edge material and some noise. This supports a preliminary
**38 × 46 mm packaging allowance**, not an exact glass outline. The body region
reaches approximately **4 mm above the fitted support plane**. Its hidden front
face, contact with the support and reflective-surface reconstruction are unknown;
surface height is not automatically physical panel thickness.

The scan-only study budgeted **4.2 mm for the combined display/touch stack**,
replacing the earlier 2.4 mm guess. The user then supplied a more specific
approximate stack: **0.25 mm cover + 0.70 mm sensor + 2.15 mm LCD/backlight =
3.10 mm, excluding tape**. The active model now adds **0.20 mm tape** for a
**3.30 mm panel assembly**, resulting in an **11.3 mm enclosure**. The same
battery thickness and rear allowance are retained. The 10.4 mm early and
12.2 mm scan-only parameter snapshots are retained as reference-only files.
The scan has not been rescaled to force agreement with the supplied thickness.
Neither source establishes a manufacturer-certified maximum stack dimension.

The mesh shows a body with rounded corners and folded tail regions extending
roughly 15–20 mm beyond its lower end. Parts of the folded region rise around
8–9 mm above the support. Scan smoothing joins thin surfaces and the support,
so the geometry cannot resolve individual conductors, 0.3 versus 0.5 mm pitch,
true film thickness, pin numbering, connector latch features or reliable bend
radii. We have **not** counted scan polygons as physical connector contacts.

The OBJ refers to `Scaniverse_2026_09_12_145606.mtl`, which is absent beside the
OBJ; the matching texture images are absent too. Consequently this inspection
is geometry-only. The original UV coordinates do not recover missing color or
printed flex codes. The scan does not establish the display controller or pinout.

The user subsequently specified **15-pin / 0.3 mm display FPC** and **6-pin /
0.5 mm touch FPC**. T01 uses these as supplied connector specifications; they
were not measured from the scan. Contact side and numbered pinout remain open.

The reported “4.3 × 3.6” is interpreted as centimetres (43 × 36 mm), and the
user has confirmed that it describes the entire outer glass surface. T01 now
uses a **36 × 43 mm** outer-glass allowance; the active-pixel aperture remains
unmeasured. The earlier 38 × 46 mm allowance remains only in the reference
snapshots.

The cropped PLY and viewer are inspection references, not a watertight physical
part used for collision certification. T01's validation uses conservative
parametric envelopes and explicit routing reserves. The ribbons will need a
new, physically checked fold into those reserves; their scanned resting pose
has not been demonstrated to fit the enclosure or reach either assumed ZIF.

To replace the provisional allowances, confirm outer glass width/height, total
stack thickness and one ribbon length with a ruler/caliper, then inspect the
matching material/texture files if available. Do not rescale the scan to match
a presumed 2.01-inch visible area; that would make the measurement circular.

Rebuild from the repository root:

```sh
.venv/bin/python touchscreen_01/scan/inspect_scan.py
.venv/bin/python touchscreen_01/scan/make_viewer.py
```
