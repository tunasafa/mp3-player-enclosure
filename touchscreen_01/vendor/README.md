# Sources and attribution

The exact unscaled Seeed XIAO ESP32-S3 STEP is reused from
[`../../revision_04/vendor/`](../../revision_04/vendor/README.md), which records
the official download, provenance and publisher terms. T01 transforms it as:
Xcase = −Zvendor − 6.1114 + Xboard;
Ycase = −Xvendor + Yboard + 1.80475;
Zcase = Yvendor + 0.25 + Zboard.
This directs USB toward the bottom. The same transform drives CAD validation
and the colored viewer model. All other electronics are labeled assumed envelopes.

Rear branding reuses the existing mytunas contour artwork in
`revision_04/assets/mytunas-branding.json`.

The offline viewer reuses the repository's Three.js 0.180.0 and Lucide 0.468.0
dependencies and P04 camera/control implementation. Their notices from
`revision_04/vendor/LICENSE-viewer.txt` are embedded in `preview.html`.
Building uses the dependencies pinned in `revision_04/package-lock.json`.
