"""Draw the actual P04 shell meshes and the thickness stack, in millimetres."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
import trimesh

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT/'parameters.json').read_text())
BG, INK, MUTED = '#f5f4f0', '#182a34', '#5c6d75'

def projected_shell(ax, name, rear=False):
    mesh = trimesh.load_mesh(ROOT/'designs/P04_compact/reference_only'/f'{name}.stl')
    # Depth-sorted orthographic projection of the exported assembly geometry.
    tri = mesh.triangles
    order = tri[:,:,2].mean(axis=1).argsort()
    if not rear:
        order = order[::-1]
    tri = tri[order]
    shade = mesh.face_normals[order,2]
    colors = [(0.79+.13*abs(n), .82+.1*abs(n), .79+.11*abs(n)) for n in shade]
    ax.add_collection(PolyCollection(tri[:,:,:2], facecolors=colors, edgecolors='none'))
    # Sharp edges show supports, apertures and fastener wells without triangle noise.
    edges = mesh.face_adjacency_edges[mesh.face_adjacency_angles > .55]
    if name == 'rear_shell' and not rear:
        # The exterior engraving is hidden by the skin in this inside projection.
        floor = P['body']['thickness']-P['branding']['depth']
        edges = edges[~(mesh.vertices[edges][:,:,2] >= floor-1e-4).all(axis=1)]
    from matplotlib.collections import LineCollection
    ax.add_collection(LineCollection(mesh.vertices[edges][:,:,:2], colors='#60746e', linewidths=.45))
    ax.set(xlim=(-43,43), ylim=(-74,74), aspect='equal')
    ax.axis('off')

def main():
    fig = plt.figure(figsize=(16.54,11.69), facecolor=BG)
    fig.text(.06,.94,'FORM 04 / COMPACT FIT PROTOTYPE',fontsize=23,color=INK,weight='bold')
    b=P['body']
    fig.text(.06,.906,f"{b['length']:g} × {b['width']:g} × {b['thickness']:g} mm  ·  repacked with unchanged components  ·  no middle carrier",fontsize=12,color=MUTED)
    for left, title, part, rear in [(.045,'FRONT SHELL / INSIDE','front_bezel',True),(.35,'REAR SHELL / INSIDE','rear_shell',False)]:
        ax=fig.add_axes([left,.23,.29,.62]); projected_shell(ax,part,rear)
        ax.set_title(title,fontsize=12,pad=12,color=INK)
    fig.text(.075,.205,'Lens recess, wheel aperture and local UI pads.\nFour blind insert bosses; two locating tongues.',fontsize=10,color=MUTED,linespacing=1.5)
    fig.text(.38,.205,'Board pads, insertion fences and 503040 battery guides.\nViewed through front; same X/Y on both drawings.',fontsize=10,color=MUTED,linespacing=1.5)
    ax=fig.add_axes([.7,.46,.235,.32],facecolor=BG)
    boards={e['id']:e for e in P['electronics']}
    d,b,q=P['display'],P['battery'],P['wheel']
    stacks=[('LCD',d['z'],d['z']+d['size'][2],'#426874'),
            ('Wheel',q['backing_z'],q['backing_z']+q['backing'][2],'#83a195'),
            ('Battery',b['z'],b['z']+b['size'][2],'#d8af55'),
            ('DAC',boards['dac']['z'],boards['dac']['z']+boards['dac']['size'][2],'#998fae')]
    for i,(label,start,end,color) in enumerate(stacks):
        ax.add_patch(Rectangle((i-.32,0),.64,1.2,facecolor='#c2cbc4'))
        ax.add_patch(Rectangle((i-.32,P['body']['thickness']-1.2),.64,1.2,facecolor='#c2cbc4'))
        ax.add_patch(Rectangle((i-.3,start),.6,end-start,facecolor=color))
    ax.set(ylim=(14,0),xlim=(-.6,3.6),ylabel='Assembly Z / mm (front → rear)')
    ax.set_xticks(range(len(stacks)),[s[0] for s in stacks],rotation=30,ha='right',fontsize=8)
    ax.set_title('COMPONENT DEPTH RANGES',fontsize=11,pad=15)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
    validation=json.loads((ROOT/'validation.json').read_text())
    c=validation['nominal_clearances_mm']
    fig.text(.7,.31,f"Clickwheel adapter to wall: {c['fpc8_to_sidewall']:.2f} mm.\nBattery to rear skin: {c['battery_to_rear_skin']:.1f} mm.\nDAC to LCD / rear skin: {c['dac_to_display']:.1f} / {c['dac_to_rear_skin']:.1f} mm.\nThese gaps still need real-part verification.",fontsize=9.5,color=MUTED,linespacing=1.6)
    fig.text(.7,.19,'115 x 60 x 12.9 mm; 0.2 mm thinner than 13.1 mm.\nBattery entirely below LCD; no footprint growth.\nFlipped upper DAC; 1.0 mm local LCD seat floor.',fontsize=10,color=INK,linespacing=1.6)
    fig.text(.06,.09,'CAD/mesh checks passed. The component envelopes and connector positions remain provisional.',fontsize=11,color=INK)
    fig.text(.06,.058,'Print an empty-shell fit set first. Exact wheel/LCD geometry, flex routes, audio mounting and battery sample fit are still required.',fontsize=10,color=MUTED)
    fig.savefig(ROOT/'design_overview.png',dpi=180,facecolor=BG)
    fig.savefig(ROOT/'design_overview.pdf',facecolor=BG)
    plt.close(fig)
    print('Created P04 design_overview.png and .pdf')

if __name__=='__main__':
    main()
