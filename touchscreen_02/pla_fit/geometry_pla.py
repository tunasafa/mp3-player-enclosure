"""M02-P01: exact-envelope PLA fit fixture; all coordinates in mm.

Purchased components and their placements come unchanged from M02-03.
This is a separate fabrication branch, not a material substitution release.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import geometry as metal
from geometry import block, rounded, cyl, ring, bounds, compound, cq, np
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box

ROOT = Path(__file__).resolve().parent
SKIN = .4
LID_Z = 7.9
SNAP_LENGTH = 18.0
SNAP_WIDTH = .8
SNAP_DEFLECTION = .7
SNAP_X = -12.0


def bounds(shape):
    # Do not let meshing deflection enlarge recorded CAD/print-bed bounds.
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape.val().wrapped, box, False, False)
    b = box.Get()
    return [list(b[:3]), list(b[3:])]


def snap_tooth(sign=1):
    # YZ section: lead-in on underside; horizontal retaining shoulder on top.
    # Tongue bends IN THE PRINT PLANE, not across a short vertical layer stack.
    points = [(61.7, 6.6), (62.1, 6.6), (62.8, 7.1),
              (62.8, 7.5), (61.7, 7.5)]
    s = cq.Workplane('YZ').polyline(points).close().extrude(2.4).translate((5.6+SNAP_X, 0, 0))
    return s if sign == 1 else s.mirror('XZ')


def make():
    original, original_visual, original_meta = metal.physical()
    # Keep EVERY original component unchanged. Adhesives remain real sheet/tape,
    # not implausibly thin printed objects. Carrier replaces its old adhesive bed.
    parts = {n: s for n, s in original.items() if original_meta[n]['kind'] == 'component'}
    tape_ids = ['display_adhesive', 'display_cushion', 'audio_insulator',
                'cell_A_envelope_adhesive', 'cell_B_envelope_adhesive',
                'pack_protection_pad', 'xiao_saddle_pad']
    parts.update({n: original[n] for n in tape_ids})
    meta = {n: dict(original_meta[n]) for n in parts}
    visual = {n: original_visual[n] for n in parts}
    printed = {}

    # A single front tray. Flat 0.4 mm floor prints on the bed; the former
    # front bond is replaced by a continuous polymer connection to the wall.
    front = rounded(64, 128, .4, 6).cut(
        rounded(*metal.D['window'], 1, .35, *metal.D['window_center'], -.2))
    wall = rounded(64, 128, 7.5, 6, z=.4).cut(rounded(60.8, 124.8, 9, 4.4, z=.3))
    u, j, sd = (metal.port_specs()[n] for n in ['usb', 'jack', 'microsd'])
    wall = wall.cut(block(4, 12, 4.8, 29, u['center'][1], u['center'][2]-2.4))
    wall = wall.cut(block(8, 4, 6.2, j['center'][0], -61, j['center'][2]-3.1))
    wall = wall.cut(block(4, 15, 3, -29, 29, sd['center'][2]-1.5))
    wall = wall.cut(block(.9, 28, 3.5, 30.45, 39, 2.3))
    for tool in metal.port_tools().values():
        wall = wall.cut(tool)
    # Two latch windows, not screw holes. Open through the edge for inspection
    # and release; 0.4 mm roof above the shoulder. No exterior protrusions.
    for sign in [-1, 1]:
        wall = wall.cut(block(3.0, 2.2, .8, 6.8+SNAP_X, sign*63.2, 6.8))
    tray = front.union(wall)

    # Low battery fences: no feature crosses either expansion volume.
    for yy in [-19.4, 7.4]:
        tray = tray.union(block(40.5, .8, 1.2, -10.75, yy, .4))
    tray = tray.union(block(.8, 26, 1.2, -29.65, -6, .4))
    for xx in [-29.15, -2.35]:
        tray = tray.union(block(.8, 38.6, 1.2, xx, -40.5, .4))
    for yy in [-59.65, -21.35]:
        tray = tray.union(block(29.4, .8, 1.2, -16.6, yy, .4))
    # DAC fences use the old inner locating faces and do not enter its CAD.
    for xx in [1.4, 28.2]:
        tray = tray.union(block(.8, 33.7, 1.7, xx, -46.3, .4))
    for yy in [-19.65, -.45]:
        tray = tray.union(block(22.7, .8, 1.7, 19.75, yy, .4))
    # Integrated flat XIAO bed replaces the loose 0.35 mm insulating seat.
    tray = tray.union(block(20.9, 17.7, .35, *metal.P['xiao']['center'], .4))
    # Four rectangular carrier shelves, outside the LCD outline. These are
    # solid loading ledges, without bored cylindrical screw towers.
    for xx in [-28.5, 28.5]:
        for yy in [11.5, 58.5]:
            tray = tray.union(block(5.4, 3, 3.95, xx, yy, .4))
    for reserve in ['cell_link_route', 'cell_link_turn']:
        tray = tray.cut(metal.reserves()[reserve])

    # Carrier is a flat printable deck, using the previous steel + tape depth.
    # Its board support plane remains Z4.85, and LCD cushion stays at Z4.30.
    carrier = rounded(59, 50, .5, 1, 0, 35, 4.35)
    carrier = carrier.cut(block(7, 29, 2, 26, 39, 4.2))
    for yy in [26, 44]:
        carrier = carrier.cut(rounded(8, 9, 2, 1, 3.5, yy, 4.2))
    # Outside-board stiffening rails: >=0.8 mm instead of 0.3 mm welded blades.
    for yy in [15, 57]:
        carrier = carrier.union(block(54, .9, .9, -1, yy, 4.85))
    carrier = carrier.union(block(.9, 40, .9, -4.5, 35.5, 4.85))
    # Board pockets are bounded on all sides, with 0.2 mm nominal lateral play.
    for yy in [19.4, 38.6]:
        carrier = carrier.union(block(21.6, .8, .8, -18.9, yy, 4.85))
    carrier = carrier.union(block(.8, 18.8, .8, -7.3, 29, 4.85))
    # SD outside edge is bounded by the enclosure's port lip.
    for yy in [22.4, 55.6]:
        carrier = carrier.union(block(15.8, .8, .8, 21, yy, 4.85))
    for xx in [12.9, 29.1]:
        # Tail side deliberately has a routing window instead of a long fence.
        for yy in [24, 54]:
            carrier = carrier.union(block(.8, 2.4, .8, xx, yy, 4.85))
    # Four tabs locate the lift-out carrier in open-top wall pockets.
    for xx in [-29.7, 29.7]:
        for yy in [11.5, 58.5]:
            carrier = carrier.union(block(1.4, 2.4, .5, xx, yy, 4.35))
            tray = tray.cut(block(1.8, 2.8, 4, xx, yy, 4.35))

    # Thin rear skin, strengthened only where component/expansion space allows.
    lid = rounded(64, 128, .4, 6, z=7.9)
    # Free each 18 mm cantilever along both sides and tip, including the skin.
    for sign in [-1, 1]:
        for yy in [60.95, 62.45]:
            lid = lid.cut(block(18.6, .7, 1, -.7+SNAP_X, sign*yy, 7.7))
        lid = lid.cut(block(.6, 2.2, 1, 8.3+SNAP_X, sign*61.7, 7.7))
        beam = block(18, .8, 1.7, -1+SNAP_X, sign*61.7, 6.6)
        # Root connects to uncut skin. Both beams stay left of the DAC, also
        # during release deflection; no component is used as a spring stop.
        root = block(1.6, 1.2, 1.3, -10.4+SNAP_X, sign*61.7, 6.6)
        lid = lid.union(beam).union(root).union(snap_tooth(sign))
    # Alignment skirt: short open segments, all inside the original envelope.
    # Deliberately avoid ports, screen tail, board connectors and battery space.
    for xx in [-29.8, 29.8]:
        for yy in [-42, 2]:
            lid = lid.union(block(.8, 8, 1.2, xx, yy, 6.7))
    # Lid captures carrier and board pocket contents; no screwed clamps.
    for xx in [-20, 20]:
        lid = lid.union(block(3, 2, 2.9, xx, 58.5, 5.0))
    for xx, yy in [(-9.5, 23), (-9.5, 35), (14.6, 24), (14.6, 53)]:
        lid = lid.union(block(1.0, 1.6, 2.1, xx, yy, 5.8))
    # Three integrated rounded rectangular pads use existing DAC mounting
    # annuli, with 0.15 mm lift clearance above the PCB. No pins or screw bores.
    for x, y, z in metal.dac_points(np.array([[2.54,22.86,0],[29.21,2.54,0],[29.21,22.86,0]])):
        pad = rounded(3, 2, 5.63, .4, x, y, 2.27)
        lid = lid.union(pad)
    # Upper DAC end stop arrives with the lid, so it cannot obstruct the
    # board's +2 mm loading offset. It prevents the unplugging direction drift.
    lid = lid.union(block(5, .8, 7.3, 20, -29.45, .6))
    lid = lid.union(block(2, 8, 3.6, 22, -10, 4.3))
    # The separate XIAO insertion gate goes in AFTER sliding USB into its port.
    gate = block(.8, 14, 1.7, 8.5, -9.25, .55)
    parts['gate_tape'] = block(.8, 14, .15, 8.5, -9.25, .4)
    meta['gate_tape'] = dict(label='Removable gate tape / 0.15 mm', kind='seal', explode=3,
                             source='Cut tape, not a printed part')
    visual['gate_tape'] = [('#c9b579', parts['gate_tape'])]
    lid = lid.union(block(.8, 5, 5.5, 8.5, -9.25, 2.4))

    for name, s, label, color, explosion in [
        ('front_tray', tray, 'PLA front tray / integral frame and locating rails', '#4c7776', -12),
        ('rear_lid', lid, 'PLA rear lid / two releasable snap tongues', '#ccd8d4', 42),
        ('carrier', carrier, 'PLA lift-out display and board carrier', '#dfb574', 12),
        ('xiao_gate', gate, 'PLA removable USB-board stop', '#dfb574', 9),
    ]:
        s = s.clean()
        parts[name] = printed[name] = s
        meta[name] = dict(label=label, kind='structure', explode=explosion,
                          source='M02-P01 / PLA / MK3S+ 0.4 mm nozzle / physical fit untested')
        visual[name] = [(color, s)]
    return parts, visual, meta, printed, metal.reserves(), original


def print_pose(name, shape):
    s = shape.rotate((0, 0, 0), (1, 0, 0), 180) if name in ['rear_lid', 'coupon_lid'] else shape
    if name == 'xiao_gate':
        s = s.rotate((0, 0, 0), (0, 1, 0), 90)
    b = bounds(s)
    return s.translate(tuple(-q for q in b[0]))


def coupons(printed):
    crop = block(26, 7, 4, -1+SNAP_X, 61, 5.8)
    receiver = printed['front_tray'].intersect(crop)
    receiver = receiver.union(block(26, 7, .6, -1+SNAP_X, 60.5, 5.8))
    cap = printed['rear_lid'].intersect(crop)
    return {'coupon_receiver': receiver.clean(), 'coupon_lid': cap.clean()}
