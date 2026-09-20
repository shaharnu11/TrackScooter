#!/usr/bin/env python3
"""Throwaway: draws the lower-shock-bolt cross-section, before and after the outer plate."""
S = 5.6          # px per mm
X0, ZMIN = 95.0, -56.0
STEEL, BOLT, PIPE, SHOCK, NEW, RED, GRN = "#7d8ea6", "#9aa1ab", "#c98a45", "#3d4450", "#2e9e4f", "#c62828", "#1e7a3c"


def X(z):
    return X0 + (z - ZMIN) * S


def Y(cy, mm):
    return cy + mm * S


def box(z0, z1, cy, m0, m1, fill, sw=1.5, rx=0):
    return (f'<rect x="{X(z0):.1f}" y="{Y(cy, m0):.1f}" width="{(z1 - z0) * S:.1f}" '
            f'height="{(m1 - m0) * S:.1f}" rx="{rx}" fill="{fill}" stroke="#2b3340" stroke-width="{sw}"/>')


def txt(x, y, s, size=17, fill="#1b2430", anchor="middle", weight="400"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="Helvetica Neue,Arial" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>')


def panel(cy, fix):
    g, nut = [], (86 if fix else 78)
    g.append(box(-52, -45, cy, -6.5, 6.5, BOLT, rx=2))                     # head
    g.append(box(-45, nut + 9, cy, -4, 4, BOLT, sw=1.2, rx=2))             # bolt shank
    for z0, z1 in ((-31.75, -25.4), (25.4, 31.75)):                        # arm fork plates
        g.append(box(z0, z1, cy, -20, 20, STEEL))
    g.append(box(31.75, 68, cy, -7.5, 7.5, PIPE, rx=2))                    # spacer pipe
    g.append(box(68, 78, cy, -11, 11, SHOCK, rx=2))                        # shock eye
    g.append(f'<circle cx="{X(73):.1f}" cy="{cy}" r="{4 * S:.1f}" fill="none" stroke="#e8edf3" stroke-width="2"/>')
    g.append(box(68, 78, cy, -32, -11, SHOCK, rx=2))                       # shock body
    for i in range(4):                                                     # coil hint
        g.append(f'<ellipse cx="{X(73):.1f}" cy="{Y(cy, -36 - i * 6):.1f}" rx="{6.6 * S:.1f}" ry="6" '
                 f'fill="none" stroke="#69727f" stroke-width="5"/>')
    g.append(txt(X(73) - 70, Y(cy, -44), "shock", 16, "#3d4450", anchor="end"))
    if fix:
        g.append(box(18, 80, cy, 20, 26, NEW))                             # welded foot
        g.append(box(80, 86, cy, -20, 26, NEW))                            # THE NEW PLATE
        for zz in (25.4, 31.75):                                           # fillet welds
            g.append(f'<polygon points="{X(zz):.1f},{Y(cy, 20):.1f} {X(zz) + 11:.1f},{Y(cy, 20):.1f} '
                     f'{X(zz):.1f},{Y(cy, 20) - 11:.1f}" fill="#d94a2b"/>')
    g.append(box(nut, nut + 7, cy, -6.5, 6.5, BOLT, rx=2))                 # nut
    # force: the shock pushes down into the eye
    fx = X(73) + 9.5 * S
    g.append(f'<line x1="{fx:.1f}" y1="{Y(cy, -46):.1f}" x2="{fx:.1f}" y2="{Y(cy, -13):.1f}" '
             f'stroke="{RED}" stroke-width="4" marker-end="url(#aD)"/>')
    g.append(txt(fx + 14, Y(cy, -46), "2681 N", 16, RED, anchor="start", weight="600"))
    return "\n".join(g)


def dim(z0, z1, y, label, col):
    x0, x1 = X(z0), X(z1)
    return (f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{col}" stroke-width="2" '
            f'marker-start="url(#aL)" marker-end="url(#aR)"/>'
            + f'<line x1="{x0}" y1="{y - 8}" x2="{x0}" y2="{y + 8}" stroke="{col}" stroke-width="2"/>'
            + f'<line x1="{x1}" y1="{y - 8}" x2="{x1}" y2="{y + 8}" stroke="{col}" stroke-width="2"/>'
            + txt((x0 + x1) / 2, y + 26, label, 16, col, weight="600"))


W, H, cy1, cy2 = 1180, 1080, 300, 790
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<defs>',
     f'<marker id="aL" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M9,0 L9,9 L0,4.5 z" fill="{RED}"/></marker>',
     f'<marker id="aR" markerWidth="9" markerHeight="9" refX="1" refY="4.5" orient="auto"><path d="M0,0 L0,9 L9,4.5 z" fill="{RED}"/></marker>',
     f'<marker id="aD" markerWidth="11" markerHeight="11" refX="5.5" refY="10" orient="auto"><path d="M0,0 L11,0 L5.5,11 z" fill="{RED}"/></marker>',
     '</defs>', f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
     txt(W / 2, 38, "Lower shock bolt — cut through the arm, looking along the arm", 21, weight="700"),
     txt(W / 2, 62, "left = far side of the pod  ·  right = outside  ·  positions in mm from the pod centre", 15, "#67707d"),
     f'<line x1="40" y1="545" x2="{W - 40}" y2="545" stroke="#dfe4ea" stroke-width="2"/>']

o += [txt(55, 110, "NOW", 20, RED, anchor="start", weight="700"),
      txt(120, 110, "— both plates are on the SAME side of the shock", 18, anchor="start"),
      txt(W - 55, 110, "351 MPa — FAILS (limit 235)", 19, RED, anchor="end", weight="700"),
      panel(cy1, False),
      dim(31.75, 73, Y(cy1, 40), "41 mm hanging out past the last plate", RED),
      txt(X(31.75), Y(cy1, 27), "last plate", 15),
      txt(X(88), Y(cy1, -30), "nothing", 15, RED, anchor="start", weight="600"),
      txt(X(88), Y(cy1, -24), "out here", 15, RED, anchor="start", weight="600")]

o += [txt(55, 600, "FIX", 20, GRN, anchor="start", weight="700"),
      txt(112, 600, "— add one plate OUTSIDE the shock, so the shock sits between two supports", 18, anchor="start"),
      txt(W - 55, 600, "51 MPa — SAFE", 19, GRN, anchor="end", weight="700"),
      panel(cy2, True),
      dim(31.75, 80, Y(cy2, 40), "shock now sits inside this span", GRN),
      txt(X(83), Y(cy2, -26), "NEW PLATE", 16, GRN, weight="700"),
      txt(X(50), Y(cy2, 33), "foot welded along the arm's bottom edge", 15, GRN),
      txt(X(28) - 10, Y(cy2, 15), "weld", 14, "#d94a2b", anchor="end")]

o += [txt(W / 2, H - 30, "Same shock, same pipe, same hole in the arm. One new piece of 40 × 6 flat bar per arm, plus a longer M8 bolt — four sets in total.", 16, "#67707d"),
      '</svg>']
open("_fig.html", "w").write("<html><body style='margin:0'>" + "\n".join(o) + "</body></html>")
