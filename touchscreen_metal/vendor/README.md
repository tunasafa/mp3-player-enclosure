# T03 component and library sources

Actual unscaled Seeed and Adafruit STEP sources remain in `../../revision_04/vendor/`, with their [provenance and license notes](../../revision_04/vendor/README.md). Adafruit geometry is MIT-licensed; the Seeed model retains its publisher attribution/terms. No component is flattened or removed for T03.

The Adafruit model is rotated −90° about Z and translated by `geometry.py`; the XIAO is rotated +90° about X. Manufacturer face meshes are cached in original coordinates and receive the same rigid transforms as the collision-checked CAD. Other components and mounting hardware are explicitly nominal construction geometry.

The Adafruit board's full published 7.1 mm height is retained even though the STEP is shorter. [Adafruit product specification](https://www.adafruit.com/product/6309). The proposed rear film uses a 0.07 mm allocation consistent with the [0.069 mm 3M 5413 thickness specification](https://www.3m.com/3M/en_US/p/dc/v000091658/); product suitability is not established by thickness alone.

Three.js and Lucide come from P04's pinned dependencies. License notices are embedded in the offline HTML and retained at `../../revision_04/vendor/LICENSE-viewer.txt`.
