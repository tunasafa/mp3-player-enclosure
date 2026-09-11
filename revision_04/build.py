"""P04 compact fit prototype. Run ../.venv/bin/python build.py from this folder.
Assembly Z goes from front to back; print STLs are individually placed at Z=0.
"""
from pathlib import Path
import json
import math
import itertools
import hashlib
import cadquery as cq
import trimesh
ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / "parameters.json").read_text())
B, F = P["body"], P["fasteners"]
W, L, T = B["width"], B["length"], B["thickness"]
SKIN, WALL, FRONT = B["skin"], B["wall"], B["front_height"]
FASTENERS = [(s*F["x"], y) for s in [-1, 1] for y in F["y"]]
OUT = ROOT / "designs" / "P04_compact"

def block(w, l, h, x=0, y=0, z=0):
    return cq.Workplane("XY").box(w, l, h, centered=(True, True, False)).translate((x, y, z))

def rounded(w, l, h, r, x=0, y=0, z=0):
    v = block(w, l, h)
    if r > 0:
        v = v.edges("|Z").fillet(min(r, w/2-.001, l/2-.001))
    return v.translate((x, y, z))

def cylinder(r, h, x=0, y=0, z=0):
    return cq.Workplane("XY").circle(r).extrude(h).translate((x, y, z))

def x_port(w, h, x, y, z, r=.6, depth=8):
    # Local X -> assembly Y, local Y -> assembly Z, local Z -> assembly X.
    s = rounded(w, h, depth, r)
    return s.rotate((0, 0, 0), (1, 1, 1), 120).translate((x, y, z))

def x_round_port(d, x, y, z, depth=8):
    return cylinder(d/2, depth).rotate((0, 0, 0), (0, 1, 0), 90).translate((x, y, z))

def stl_export(shape, path, rear=False):
    a = shape
    if rear:
        a = a.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = a.val().BoundingBox()
    a = a.translate((-bb.xmin, -bb.ymin, -bb.zmin))
    cq.exporters.export(a, str(path), tolerance=.035, angularTolerance=.12)
    mesh = trimesh.load_mesh(path, process=True)
    valid = bool(a.val().isValid())
    entry = {"file": str(path.relative_to(ROOT)), "bounds_mm": mesh.extents.tolist(),
             "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
             "solid_count_cad": len(a.solids().vals()), "mesh_bodies": int(mesh.body_count),
             "positive_volume": bool(mesh.volume > 0), "cad_valid": valid,
             "volume_mm3": float(mesh.volume), "faces": len(mesh.faces)}
    if not (entry["watertight"] and entry["winding_consistent"] and entry["positive_volume"] and valid
            and entry["solid_count_cad"] == 1 and entry["mesh_bodies"] == 1):
        raise RuntimeError(f"Invalid STL: {entry}")
    return entry

def collisions(parts, components):
    result = []
    physical = dict(parts, **components)
    for (na, a), (nb, b) in itertools.combinations(physical.items(), 2):
        ba, bb = a.val().BoundingBox(), b.val().BoundingBox()
        if any(getattr(ba, f"{k}max") <= getattr(bb, f"{k}min")+1e-6 or
               getattr(bb, f"{k}max") <= getattr(ba, f"{k}min")+1e-6 for k in "xyz"):
            continue
        vol = a.intersect(b).val().Volume()
        if vol > .001:
            result.append({"a": na, "b": nb, "intersection_mm3": vol})
    return result

def make_coupon():
    a = rounded(58, 28, 5.2, 3)
    for x, d in [(-20, 3.0), (-10, 3.1), (0, 3.2), (10, 3.3), (20, 3.4)]:
        a = a.cut(cylinder(d/2, 3.3, x, 4, 2.0))
    for x, d in [(-18, 2.1), (-6, 2.2), (6, 2.3), (18, 2.4)]:
        a = a.cut(cylinder(d/2, 7, x, -7, -1))
    return a

def outer(h, z=0, rear=False):
    return rounded(W, L, h, B['corner_radius'], z=z).faces('>Z' if rear else '<Z').edges().fillet(.4)

def cavity(z, h):
    return rounded(W-2*WALL, L-2*WALL, h, B['corner_radius']-WALL, z=z)

def boss(x, y, z, top):
    edge = math.copysign(W/2-.4, x)
    return cylinder(F['boss_radius'], top-z, x, y, z).union(
        block(abs(edge-x)+.4, 1.8, top-z, (x+edge)/2, y, z))

def ports(a):
    boards = {e['id']: e for e in P['electronics']}
    for key, board in [('usb', 'xiao'), ('microsd', 'microsd')]:
        p = P['ports'][key]
        a = a.cut(x_port(p['width'], p['height'], W/2-4,
                         boards[board]['center'][1], p['z']))
    p = P['ports']['jack']
    dac = boards[p['board']]
    hole = cylinder(p['diameter']/2, 8).rotate((0,0,0), (1,0,0), -90)
    return a.cut(hole.translate((dac['center'][0]+p['axis_offset_x'],
                                L/2-4, dac['z']+p['axis_offset_z'])))

def front_shell():
    a = outer(FRONT).cut(cavity(SKIN, FRONT+1))
    for x, y in FASTENERS:
        a = a.union(boss(x, y, .8, FRONT))
        a = a.cut(cylinder(F['insert_pilot_diameter']/2, F['insert_depth']+.1,
                          x, y, FRONT-F['insert_depth']))
    d, q = P['display'], P['wheel']
    a = a.cut(rounded(*d['window'], FRONT+2, .5, y=d['window_y'], z=-1))
    a = a.cut(rounded(d['window'][0]+2.4, d['window'][1]+2.4, .9, .9,
                      y=d['window_y'], z=-.1))
    a = a.cut(cylinder(q['aperture_diameter']/2, FRONT+2, *q['center'], z=-1))
    # Local landing pads; 0.2 mm adhesive allowance to assumed component fronts.
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            a = a.union(block(3, 4, d['z']-.2-1.0, sx*23.5, d['center'][1]+sy*16, 1.0))
            a = a.union(block(3, 4, q['backing_z']-.2-1.0, sx*25, q['center'][1]+sy*25, 1.0))
    # Interrupted locating tongues leave the UI flex exits and ports clear.
    for sx in [-1, 1]:
        a = a.union(block(.8, 24, 2.0, sx*(W/2-2.5), 32, FRONT-.8))
        a = a.union(block(1.8, 24, .8, sx*(W/2-1.9), 32, FRONT-.8))
    return ports(a).clean()

def rear_shell():
    start = FRONT+B['seam_gap']
    inner = T-SKIN
    a = outer(T-start, start, True).cut(cavity(start-1, inner-start+1))
    # Bosses reach the front's hard stops; seam clearance does not carry clamp load.
    for x, y in FASTENERS:
        a = a.union(boss(x, y, FRONT, T-.7))
        a = a.cut(cylinder(F['clearance_diameter']/2, T+2, x, y, 0))
        a = a.cut(cylinder(F['head_recess_diameter']/2, T-F['head_seat_z']+1,
                          x, y, F['head_seat_z']))
    # Rear-mounted pads stop 0.2 mm short of board envelopes for insulating adhesive.
    for e in P['electronics']:
        x, y = e['center']; w, l, h = e['size']
        z = e['z']+h+.2
        for sx in [-1, 1]:
            for sy in [-1, 1]:
                a = a.union(block(4, 3, inner+.2-z, x+sx*(w/2-3), y+sy*(l/2-3), z))
    # Inboard fences oppose USB/card insertion. Retention still needs sample fitting.
    for e in P['electronics']:
        if e['id'] in ('xiao', 'microsd'):
            x, y = e['center']; w = e['size'][0]
            a = a.union(block(.8, 8, inner+.2-5.4, x-w/2-.6, y, 5.4))
    # Guides follow the selected battery body. Listing size is not a certified max.
    b = P['battery']; bx, by = b['center']; bw, bl, _ = b['size']
    gap, t, h = b['guide_gap_xy'], b['guide_thickness'], b['guide_height']
    for sx in [-1, 1]:
        a = a.union(block(t, bl-8, h+.2, bx+sx*(bw/2+gap+t/2), by, inner-h))
    a = a.union(block(bw-8, t, h+.2, bx, by+bl/2+gap+t/2, inner-h))
    # Fence on the DAC's inboard short edge opposes insertion at its top socket.
    dac = next(e for e in P['electronics'] if e['id']=='dac')
    a = a.union(block(8, .8, inner+.2-5.4, dac['center'][0],
                      dac['center'][1]-dac['size'][1]/2-.6, 5.4))
    return ports(a).clean()

def reference_components():
    d, q, b = P['display'], P['wheel'], P['battery']
    r = {'display_envelope': block(*d['size'], *d['center'], d['z']),
         'clickwheel_envelope': block(*q['backing'], *q['center'], q['backing_z']).union(
             cylinder(q['face_diameter']/2, 1.4, *q['center'], .2)),
         'battery_envelope': block(*b['size'], *b['center'], b['z']),
         'clear_lens_reference': rounded(d['window'][0]+2, d['window'][1]+2, .6, .8,
                                         y=d['window_y'], z=.1)}
    for e in P['electronics']:
        r[e['id']] = block(*e['size'], *e['center'], e['z'])
    return r

def main():
    for name in ['STL', 'reference_only']:
        (OUT/name).mkdir(parents=True, exist_ok=True)
    parts = {'front_bezel': front_shell(), 'rear_shell': rear_shell()}
    components = reference_components()
    report = {'revision': P['revision'], 'units': 'mm', 'outer_length_width_thickness_mm': [L,W,T],
              'scope': 'CAD/mesh, assembly interference, and designated empty routing-volume checks; no physical fit, wiring, battery expansion or load validation.',
              'stls': [], 'envelope_collisions': collisions(parts, components)}
    routes = {r['id']: block(*r['size'], *r['center'], r['z']) for r in P['routing_reserves']}
    report['routing_reserve_collisions'] = [c for c in collisions(dict(parts, **components), routes)
                                          if (c['a'] in routes) != (c['b'] in routes)]
    # Routing volumes may intentionally join each other; they must clear solids.
    assembly = cq.Assembly(name='P04_compact')
    for name, shape in parts.items():
        report['stls'].append(stl_export(shape, OUT/'STL'/f'{name}.stl', rear=name=='rear_shell'))
        cq.exporters.export(shape, str(OUT/f'{name}.step'))
    for name, shape in dict(parts, **components).items():
        cq.exporters.export(shape, str(OUT/'reference_only'/f'{name}.stl'), tolerance=.06, angularTolerance=.15)
        color = (.88,.87,.82) if name=='front_bezel' else (.45,.60,.55)
        if name=='battery_envelope': color=(.85,.68,.3)
        assembly.add(shape, name=name if name in parts else 'ASSUMED_'+name, color=cq.Color(*color))
    assembly.export(str(OUT/'assembly_with_ASSUMED_components.step'))
    report['stls'].append(stl_export(make_coupon(), OUT/'STL'/'insert_and_clearance_fit_coupon.stl'))
    cq.exporters.export(components['clear_lens_reference'].faces('<Z').wires(), str(OUT/'clear_lens_0p6_REFERENCE.dxf'))
    # Derive clearances from the actual input geometry rather than a stale report.
    boards = {e['id']: e for e in P['electronics']}
    dac, fpc, bat = boards['dac'], boards['fpc8'], P['battery']
    fpc_wall = W/2-WALL+fpc['center'][0]-fpc['size'][0]/2
    dac_display = dac['z']-(P['display']['z']+P['display']['size'][2])
    dac_rear = T-SKIN-(dac['z']+dac['size'][2])
    tip = F['head_seat_z']-F['screw_length']
    report['nominal_clearances_mm'] = {
        'fpc8_to_sidewall': round(fpc_wall, 4),
        'fpc8_to_front_shell_cad_distance': components['fpc8'].val().distance(parts['front_bezel'].val()),
        'dac_to_display': round(dac_display, 4), 'dac_to_rear_skin': round(dac_rear, 4),
        'wheel_to_battery': round(bat['z']-(P['wheel']['backing_z']+P['wheel']['backing'][2]),4),
        'battery_to_rear_skin': round(T-SKIN-(bat['z']+bat['size'][2]),4),
        'battery_to_side_guide': bat['guide_gap_xy'], 'board_support_adhesive': .2,
        'screw_tip_above_pilot_bottom': round(tip-(FRONT-F['insert_depth']),4),
        'screw_insert_engagement': round(FRONT-tip,4), 'tongue_to_rear_wall': .5,
        'dac_top_edge_to_inner_wall': round(L/2-WALL-(dac['center'][1]+dac['size'][1]/2),4),
        'dac_top_edge_to_outer_face': round(L/2-(dac['center'][1]+dac['size'][1]/2),4)}
    report['minimum_clearance_checks'] = {key: report['nominal_clearances_mm'][key]>=limit-1e-6
                                          for key,limit in P['minimum_clearances'].items()}
    report['jack_axis_assembly_mm'] = [dac['center'][0]+P['ports']['jack']['axis_offset_x'],
        L/2, dac['z']+P['ports']['jack']['axis_offset_z']]
    # Rotate vendor X toward enclosure top, Y toward right, components toward front.
    vendor = cq.importers.importStep(str(ROOT/'vendor/6309.step'))
    vendor = vendor.rotate((0,0,0), (1,1,0), 180).translate(
        (dac['center'][0]-12.7, dac['center'][1]-16.85, dac['z']+dac['size'][2]))
    vb = vendor.val().BoundingBox()
    eb = components['dac'].val().BoundingBox()
    contained = all(getattr(vb,k+'min') >= getattr(eb,k+'min')-1e-5 and
                    getattr(vb,k+'max') <= getattr(eb,k+'max')+1e-5 for k in 'xyz')
    if not contained:
        raise RuntimeError('Vendor DAC geometry exceeds conservative envelope')
    cq.exporters.export(vendor, str(OUT/'reference_only/adafruit_6309_placed_VENDOR.step'))
    mouth = [16.75915274704965-12.7+dac['center'][0],
             33.537009525569644+dac['center'][1]-16.85,
             dac['z']+dac['size'][2]-3.87248295809683]
    if abs(mouth[0]-report['jack_axis_assembly_mm'][0]) > .001 or abs(mouth[2]-report['jack_axis_assembly_mm'][2]) > .001:
        raise RuntimeError('Jack cutout does not follow vendor socket axis')
    report['vendor_dac'] = {'contained_in_planning_envelope': contained,
        'assembly_bounds_mm': [[getattr(vb,k+'min') for k in 'xyz'],[getattr(vb,k+'max') for k in 'xyz']],
        'socket_mouth_axis_mm': mouth, 'socket_mouth_recess_mm': L/2-mouth[1],
        'orientation': 'PCB back toward rear; components toward display',
        'note': 'Vendor STEP height 6.3725mm; reserved published product height 7.1mm. Physical sample unmeasured.'}
    report['input_sha256'] = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                              for name in ['build.py','parameters.json','vendor/6309.step']}
    (ROOT/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    if report['envelope_collisions'] or report['routing_reserve_collisions'] or not all(report['minimum_clearance_checks'].values()):
        raise RuntimeError(json.dumps(report, indent=2))
    print('P04: all 3 printable STLs valid, single-body, watertight; no modeled collisions; minimum clearances passed.', flush=True)

if __name__ == '__main__':
    main()
