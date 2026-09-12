# Detached-jack experiment: not selected

The active P04 design retains the complete Adafruit #6309 and its onboard jack.
On 2026-09-12 the user clarified that connector removal is useful only if it
reduces the complete device's thickness or footprint. The detached SJ-3523
experiment did neither with the retained battery and front UI, so it was removed
from the active CAD, BOM, preview and manufacturing package.

`rejected-experiment.zip` preserves the experimental source, parameters, reports
and socket references. This snapshot includes an interrupted update: some tests
and prose still describe removal of only one connector while the last parameters
remove both. It is historical evidence, not a validated release or a directly
rebuildable standalone project. Do not use it as assembly instructions.

Measured from the original Adafruit STEP, nominal DAC height was 6.372483 mm
intact, 6.37 mm with only PJ-332A removed, and 3.12 mm with PJ-332A and JSTPH2
removed. Both removals therefore recover about 3.25 mm locally. They do not
remove the 12.9 mm wheel/battery stack. The detached design also adds a separate
socket footprint, retaining cradle and leads.

The preceding implementation retained the intact board's 7.1 mm planning box
even after both sockets were removed. That box should not be used to evaluate
the modified board's actual local benefit. The independent battery constraint
still explains the zero whole-case gain. Any future experiment must model the
modified board with an explicit rework/insulation allowance and assess all
remaining stacks, including the remote socket and wire routing.
