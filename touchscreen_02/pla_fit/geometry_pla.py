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
# Support-free retention: friction skirts with vertical crush ribs replace the
# former snap hooks, whose retaining shoulders printed over open air.
SKIRT_GAP = .2
RIB_R = .4
RIB_INTERFERENCE = .1
LIFT_NOTCH_X = 4.0


def bounds(shape):
    # Do not let meshing deflection enlarge recorded CAD/print-bed bounds.
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape.val().wrapped, box, False, False)
    b = box.Get()
    return [list(b[:3]), list(b[3:])]


def wedge(axis, inner, back, roof, length, along):
    """45-degree cut above a shallow wall pocket so its roof needs no support.

    `inner` is the cavity-side wall face, `back` the pocket's far face and
    `roof` its flat ceiling; the cut only removes material (more clearance).
    """
    d, e = abs(back-inner), .02
    # The slope passes exactly through the pocket's back roof edge; extending
    # it slightly past that edge leaves no flat sliver of ceiling behind.
    pts = [(inner, roof-e), (back+np.sign(back-inner)*e, roof-e), (inner, roof+d)]
    if axis == 'x':
        return cq.Workplane('XZ').polyline(pts).close().extrude(length/2, both=True).translate((0, along, 0))
    return cq.Workplane('YZ').polyline(pts).close().extrude(length/2, both=True).translate((along, 0, 0))


def rib(x, y):
    # Vertical crush rib with a conical lead-in. In the print pose the cone
    # points up, so every rib grows straight from the rear skin on the bed.
    cone = cq.Workplane('XY').newObject([cq.Solid.makeCone(.1, RIB_R, .25)]).translate((x, y, 6.75))
    return cyl(RIB_R, LID_Z-7.0, x, y, 7.0).union(cone)


def skirts():
    """(segment, ribs) pairs; segments sit SKIRT_GAP inside the tray wall."""
    out = []
    reach = RIB_R-SKIRT_GAP-RIB_INTERFERENCE
    for xx in [-29.8, 29.8]:
        face = abs(xx)+.4
        for yy in [-42, 2]:
            ribs = [rib((face-reach)*np.sign(xx), yy+dy) for dy in [-2.5, 2.5]]
            out.append((block(.8, 8, 1.2, xx, yy, 6.7), ribs))
    for sign in [-1, 1]:
        # Ends: where the old snap beams were, already clear of all components.
        ribs = [rib(xx, sign*(62.2-reach)) for xx in [-19, -13, -7]]
        out.append((block(18, .8, 1.2, -13, sign*61.8, 6.7), ribs))
    return out


def all_ribs():
    return compound([r for _, ribs in skirts() for r in ribs])


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
    # 45-degree ceilings over the shallow inner pockets (USB, recess, jack):
    # self-supporting instead of flat 0.5-0.6 mm overhangs.
    wall = wall.cut(wedge('x', 30.4, 31.0, u['center'][2]+2.4, 12, u['center'][1]))
    wall = wall.cut(wedge('x', 30.4, 30.9, 5.8, 28, 39))
    wall = wall.cut(wedge('y', -62.4, -63.0, j['center'][2]+3.1, 8, j['center'][0]))
    # Fingernail lift notches under the lid edge at both ends; open-topped.
    for sign in [-1, 1]:
        wall = wall.cut(block(10, 1.0, .7, LIFT_NOTCH_X, sign*63.5, 7.2))
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
    def deck(h):
        d = rounded(59, 50, h, 1, 0, 35, 4.35)
        d = d.cut(block(7, 29, h+1, 26, 39, 4.2))
        for yy in [26, 44]:
            d = d.cut(rounded(8, 9, h+1, 1, 3.5, yy, 4.2))
        return d
    carrier = deck(.5)
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
    # Raised features stop at the deck edge: nothing prints over open air.
    carrier = deck(.5).union(carrier.intersect(deck(3)))
    # Four tabs locate the lift-out carrier in open-top wall pockets.
    for xx in [-29.7, 29.7]:
        for yy in [11.5, 58.5]:
            carrier = carrier.union(block(1.4, 2.4, .5, xx, yy, 4.35))
            tray = tray.cut(block(1.8, 2.8, 4, xx, yy, 4.35))

    # Thin rear skin, strengthened only where component/expansion space allows.
    lid = rounded(64, 128, .4, 6, z=7.9)
    # Friction skirt: short open segments, all inside the original envelope.
    # Deliberately avoid ports, screen tail, board connectors and battery space.
    # Crush ribs give 0.1 mm interference per side against the tray wall.
    for segment, ribs in skirts():
        lid = lid.union(segment)
        for r in ribs:
            lid = lid.union(r)
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
        ('rear_lid', lid, 'PLA rear lid / friction skirts with crush ribs', '#ccd8d4', 42),
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
    # Friction-fit trial around one end skirt: same wall, ribs and lift notch.
    crop = block(24, 8, 9, -12, 60.5, -.5)
    receiver = printed['front_tray'].intersect(crop)
    cap = rounded(64, 128, .4, 6, z=7.9).intersect(crop)
    segment, ribs = skirts()[-1]
    for s in [segment]+ribs:
        cap = cap.union(s)
    return {'coupon_receiver': receiver.clean(), 'coupon_lid': cap.clean()}
