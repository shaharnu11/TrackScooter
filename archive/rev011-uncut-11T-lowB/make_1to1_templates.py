#!/usr/bin/env python3
"""
Rev 011 — generator for the 1:1 drilling templates (rev011_1to1_drilling_templates.pdf).

WHY THIS SCRIPT EXISTS
----------------------
The first version of this sheet was hand-authored HTML printed to PDF. The artwork was
geometrically perfect, but it was laid out as a full-bleed A4 page. A full-bleed page is
LARGER than any printer's printable area, so the two most common print settings —
Preview's "Scale to Fit" and Acrobat's default "Shrink oversized pages" — both silently
scale it down by 6-9%. A 165.7 mm bar prints as ~150-156 mm and the paper is scrap.

This generator fixes that structurally:

  1. The page is 195 x 259.5 mm — deliberately SMALLER than the printable area of both
     A4 (~197 x 284) and US Letter (~203 x 267). Nothing is oversized, so "Actual size"
     and "Shrink oversized pages" both produce an exact 1:1 print, and the same file is
     correct on A4 and Letter with no paper-size mismatch.
  2. Every page is ONE SVG whose user unit is exactly 1 mm, so the part, the dimensions
     and the verification rulers cannot be scaled independently of each other — if the
     ruler reads right, the part is right.
  3. Each page carries an X and a Y ruler plus a reprint-percentage table, so any
     residual scaling (an explicit "Fit to page", a driver that ignores us) is detected
     in 5 seconds and recovered in one reprint instead of being discovered in steel.

GEOMETRY SOURCE
---------------
Numbers below are the SCAD model as exported to plates_rev011.dxf. Cross-checked
polyline-by-polyline against that DXF. One correction versus the first version of the
sheet: the carrier's hub-axle key is Ø10.4 with two flats 8.9 apart and NO slot, per
apollo_track_pod_rev011.scad:641-642 and DXF polylines 3/4. The old sheet drew it as a
Ø10.4 slot with flats 9.9 apart, contradicting both the model and its own callout.

USAGE
-----
    python3 make_1to1_templates.py            # writes the HTML, renders the PDF, verifies it
"""

import math
import os
import re
import subprocess
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_OUT = os.path.join(HERE, "rev011_1to1_drilling_templates.html")
PDF_OUT = os.path.join(HERE, "rev011_1to1_drilling_templates.pdf")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Page: smaller than the printable area of BOTH A4 and Letter. Do not enlarge.
PAGE_W, PAGE_H = 195.0, 259.5
MARGIN = 5.0

INK = "#000"
RED = "#c00"
GREY = "#666"

# ---------------------------------------------------------------------------
# geometry (mm) — from plates_rev011.dxf / apollo_track_pod_rev011.scad
# ---------------------------------------------------------------------------

BAR_W = 40.0          # 40 x 6.35 (1/4") flat bar
CHAMFER = 10.0        # 10 x 10 on both corners of the pivot (rear) end
PIVOT_X = 22.0        # Ø30.8 pivot-bushing bore, from the chamfered end
BRACE_X = 73.1        # Ø8.4 brace bolt
D_PIVOT, D_BRACE, D_AXLE = 30.8, 8.4, 15.4

TRAILING = dict(
    key="trailing",
    title="TRAILING (rear) ARM BAR",
    qty="×4",
    length=183.7,
    stock="40 × 6.35 (¼″) flat bar",
    holes=[(PIVOT_X, D_PIVOT, "Ø30.8 pivot bushing"),
           (BRACE_X, D_BRACE, "Ø8.4 brace")],
    slot=(139.7, 164.7, D_AXLE),
    notes=[
        "Chamfer 10×10 on both rear corners · every hole is on the centreline, 20.0 from either edge.",
        "Wheel end is a 25 mm SLOT for the belt tensioner: drill Ø15.4 at 139.7 and at 164.7, saw out",
        "the web between them, then file the sides parallel.",
        "Cut 1 mm long at the wheel end — arm length C = 117.4 is sacred and gets filed to final",
        "position with the belt fitted (blueprint §9.2), never guessed.",
    ],
)

LEADING = dict(
    key="leading",
    title="LEADING (front) ARM BAR",
    qty="×4",
    length=165.7,
    stock="40 × 6.35 (¼″) flat bar",
    holes=[(PIVOT_X, D_PIVOT, "Ø30.8 pivot bushing"),
           (BRACE_X, D_BRACE, "Ø8.4 brace"),
           (139.7, D_AXLE, "Ø15.4 idler axle")],
    slot=None,
    notes=[
        "Chamfer 10×10 on both rear corners · every hole is on the centreline, 20.0 from either edge.",
        "Plain round axle bore Ø15.4 at the wheel end — no slot (that is the trailing bar only).",
        "The two plates of a fork are identical: clamp them together and drill them as a pair.",
        "Cut 1 mm long at the wheel end — arm length C = 117.4 is sacred and gets filed to final",
        "position with the belt fitted (blueprint §9.2), never guessed.",
    ],
)

CARRIER = dict(
    title="CARRIER PLATE",
    qty="×4",
    w=50.0, h=220.0,
    stock="50 × 6 bar · no keel hole",
    fork=(25.0, 16.0, 8.5),        # Ø8.5 M8 into the fork leg
    axle=(25.0, 68.0, 10.4, 8.9),  # Ø10.4 with flats 8.9 apart — the torque-arm key
    pivot=(25.0, 196.0, 16.0),     # Ø16 pivot axle
)

SMALL = [
    dict(title="SHOCK TAB STUB", qty="×8", w=55.0, h=40.0, hole=(44.1, 22.4, 8.4),
         note="40×6 · laps 17 mm onto the carrier OUTER face"),
    dict(title="BRACE WEB — LEADING", qty="×2", w=66.5, h=30.0, hole=None,
         note="40×6 offcut · no holes · the leading fork is the wider one"),
    dict(title="BRACE WEB — TRAILING", qty="×2", w=50.8, h=30.0, hole=None,
         note="40×6 offcut · no holes · nests inside the leading brace"),
    dict(title="TENSIONER PUSHER BLOCK", qty="×2", w=26.0, h=14.0, hole=(13.0, 7.0, 6.6),
         note="40×6 · 26 long, rip to 14 · drill 6.6 + weld M6 nut on the FORWARD face (or drill 5.0 and tap M6) — Rev 011b pusher"),
]

# ---------------------------------------------------------------------------
# svg helpers — every coordinate is millimetres
# ---------------------------------------------------------------------------


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# Lowest y touched on the page being built. Text is invisible to the PDF-side bounds
# check (that one only sees paths), so track it here and assert before rendering.
_max_y = 0.0


def _reset_extent():
    global _max_y
    _max_y = 0.0


def _note_y(*ys):
    global _max_y
    for y in ys:
        if y > _max_y:
            _max_y = y


def line(x1, y1, x2, y2, w=0.25, color=INK, dash=None):
    _note_y(y1, y2)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" '
            f'stroke="{color}" stroke-width="{w}"{d}/>')


def text(x, y, s, size=3.0, color=INK, anchor="start", weight="normal", family=None):
    _note_y(y + size * 0.28)   # allow for descenders
    fam = family or "Helvetica, Arial, sans-serif"
    return (f'<text x="{x:.3f}" y="{y:.3f}" font-family="{fam}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')


def circle(cx, cy, d, w=0.25, color=INK, fill="none", dash=None):
    _note_y(cy + d / 2)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{d / 2:.4f}" fill="{fill}" '
            f'stroke="{color}" stroke-width="{w}"{da}/>')


def rect(x, y, w, h, sw=0.25, color=INK, fill="none"):
    _note_y(y + h)
    return (f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" '
            f'fill="{fill}" stroke="{color}" stroke-width="{sw}"/>')


def poly(pts, sw=0.3, color=INK, fill="none"):
    _note_y(*[y for _, y in pts])
    p = " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{color}" stroke-width="{sw}"/>'


def hole(cx, cy, d, cross=3.0):
    """Drilled hole: true-size circle, centre cross, and a punch dot at the centre."""
    out = [circle(cx, cy, d, w=0.3, color=RED)]
    r = d / 2 + cross
    out.append(line(cx - r, cy, cx + r, cy, w=0.18, color=RED))
    out.append(line(cx, cy - r, cx, cy + r, w=0.18, color=RED))
    out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="0.6" fill="{RED}"/>')
    return out


def flatted_hole(cx, cy, d, across):
    """Ø d circle intersected with a band `across` mm tall — a flatted axle key."""
    r, a = d / 2.0, across / 2.0
    dx = math.sqrt(max(r * r - a * a, 0.0))
    steps = 64
    pts = []
    # bottom flat, then the right arc, then the top flat, then the left arc
    pts.append((cx - dx, cy + a))
    pts.append((cx + dx, cy + a))
    a0 = math.atan2(a, dx)
    for i in range(steps + 1):
        t = a0 - 2 * a0 * i / steps
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    pts.append((cx - dx, cy - a))
    a1 = math.pi - a0
    for i in range(steps + 1):
        t = a1 + 2 * a0 * i / steps
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    out = [poly(pts, sw=0.3, color=RED)]
    out.append(line(cx - r - 3, cy, cx + r + 3, cy, w=0.18, color=RED))
    out.append(line(cx, cy - r - 3, cx, cy + r + 3, w=0.18, color=RED))
    out.append(f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="0.6" fill="{RED}"/>')
    return out


def arrow(x, y, direction, size=1.6):
    s = size if direction > 0 else -size
    return poly([(x, y), (x - s, y - size * 0.42), (x - s, y + size * 0.42)],
                sw=0, color=INK, fill=INK)


def dim_h(x1, x2, y, label, size=2.7, tick=1.6):
    """Horizontal dimension between x1 and x2 with arrowheads and a centred label."""
    out = [line(x1, y - tick, x1, y + tick, w=0.18, color=GREY),
           line(x2, y - tick, x2, y + tick, w=0.18, color=GREY),
           line(x1, y, x2, y, w=0.18, color=INK)]
    out.append(arrow(x1, y, -1))
    out.append(arrow(x2, y, +1))
    out.append(f'<rect x="{(x1 + x2) / 2 - len(label) * size * 0.34:.3f}" '
               f'y="{y - size * 0.75:.3f}" width="{len(label) * size * 0.68:.3f}" '
               f'height="{size * 1.15:.3f}" fill="#fff" stroke="none"/>')
    out.append(text((x1 + x2) / 2, y + size * 0.36, label, size=size, anchor="middle"))
    return out


def dim_v(y1, y2, x, label, size=2.7, tick=1.6, backing=False):
    out = [line(x - tick, y1, x + tick, y1, w=0.18, color=GREY),
           line(x - tick, y2, x + tick, y2, w=0.18, color=GREY),
           line(x, y1, x, y2, w=0.18, color=INK)]
    cy = (y1 + y2) / 2
    if backing:  # for a dimension that runs inside the part outline
        out.append(f'<rect x="{x - size * 0.75:.3f}" '
                   f'y="{cy - len(label) * size * 0.36:.3f}" '
                   f'width="{size * 1.15:.3f}" '
                   f'height="{len(label) * size * 0.72:.3f}" fill="#fff" stroke="none"/>')
    out.append(f'<g transform="rotate(-90 {x:.3f} {cy:.3f})">'
               + text(x, cy + size * 0.36, label, size=size, anchor="middle")
               + "</g>")
    return out


def ruler_h(x, y, length, label):
    """Horizontal verification scale: 1/5/10 mm ticks, numerals every 10 mm."""
    out = [line(x, y, x + length, y, w=0.3)]
    for mm in range(0, int(length) + 1):
        if mm % 10 == 0:
            h, w = 4.2, 0.3
        elif mm % 5 == 0:
            h, w = 2.8, 0.22
        else:
            h, w = 1.5, 0.15
        out.append(line(x + mm, y, x + mm, y - h, w=w))
        if mm % 10 == 0:
            out.append(text(x + mm, y + 3.4, str(mm), size=2.5, anchor="middle"))
    out.append(line(x, y - 6.0, x, y, w=0.3))
    out.append(line(x + length, y - 6.0, x + length, y, w=0.3))
    out.append(text(x, y - 7.2, label, size=2.6, weight="bold"))
    return out


def ruler_v(x, y, length, label):
    out = [line(x, y, x, y + length, w=0.3)]
    for mm in range(0, int(length) + 1):
        if mm % 10 == 0:
            h, w = 4.2, 0.3
        elif mm % 5 == 0:
            h, w = 2.8, 0.22
        else:
            h, w = 1.5, 0.15
        out.append(line(x, y + mm, x + h, y + mm, w=w))
        if mm % 10 == 0:
            out.append(text(x + 5.2, y + mm + 0.9, str(mm), size=2.5))
    out.append(line(x - 6.0, y, x, y, w=0.3))
    out.append(line(x - 6.0, y + length, x, y + length, w=0.3))
    # label sits horizontally above the scale — rotated text here would run off the sheet
    out.append(text(x - 6.0, y - 2.4, label, size=2.6, weight="bold"))
    return out


def centreline(x1, x2, y):
    return line(x1, y, x2, y, w=0.15, color=GREY, dash="4 1.5 1 1.5")


# ---------------------------------------------------------------------------
# page furniture
# ---------------------------------------------------------------------------


def header(title, qty, stock, page_no, pages):
    o = [text(MARGIN, MARGIN + 3.4, f"REV 011 · 1:1 TEMPLATE — {title} {qty}",
              size=4.2, weight="bold"),
         text(PAGE_W - MARGIN, MARGIN + 3.4, f"{page_no}/{pages}",
              size=3.0, color=GREY, anchor="end"),
         text(MARGIN, MARGIN + 7.6, stock, size=2.8, color=GREY),
         line(MARGIN, MARGIN + 9.4, PAGE_W - MARGIN, MARGIN + 9.4, w=0.3)]
    y = MARGIN + 11.2
    o.append(rect(MARGIN, y, PAGE_W - 2 * MARGIN, 9.6, sw=0.35, color=RED))
    o.append(text(MARGIN + 2.0, y + 3.9,
                  "PRINT AT 100% / “ACTUAL SIZE” — NOT “Fit to page”, "
                  "NOT “Shrink oversized pages”.",
                  size=3.1, weight="bold", color=RED))
    o.append(text(MARGIN + 2.0, y + 7.9,
                  "A4 or US Letter both work — this page is smaller than either. "
                  "Check the ruler below BEFORE you cut or drill.",
                  size=2.7, color=RED))
    return o, y + 12.4


def scale_block(x, y, width, xlen=150.0, ylen=50.0):
    """X + Y verification rulers and the reprint-percentage recovery table."""
    o = []
    o += ruler_h(x, y + 8.0, xlen,
                 f"SCALE CHECK — this scale must measure exactly {xlen:.0f} mm")
    yy = y + 22.0
    o += ruler_v(x + 6.0, yy, ylen, f"and this one {ylen:.0f} mm")
    tx = x + 26.0
    o.append(text(tx, yy + 2.0, "If it does not measure right, do not cut — reprint.",
                  size=2.9, weight="bold"))
    o.append(text(tx, yy + 6.2,
                  f"Reprint percentage = {xlen * 100:.0f} ÷ (the mm you actually measured).",
                  size=2.7))
    o.append(text(tx, yy + 10.0,
                  "Reads LONG = the dialog is enlarging; reads SHORT = shrinking. "
                  "Either way: Actual size.",
                  size=2.5, color=GREY))
    o.append(text(tx, yy + 15.0, f"if the {xlen:.0f} mm scale reads…", size=2.5,
                  color=GREY, weight="bold"))
    o.append(text(tx + 36.0, yy + 15.0, "reprint at", size=2.5, color=GREY,
                  weight="bold"))
    # Rows scale with the ruler, and span BOTH directions: this page is smaller than
    # the paper, so "Fit to page" enlarges it — the common failure is reading long.
    for i, frac in enumerate((0.94, 0.96, 0.98, 1.00, 1.02, 1.04)):
        ry = yy + 19.0 + i * 4.0
        exact = frac == 1.00
        o.append(text(tx, ry, f"{xlen * frac:.0f} mm", size=2.7))
        o.append(text(tx + 36.0, ry,
                      "correct — go ahead" if exact else f"{100 / frac:.0f}%",
                      size=2.7, weight="bold" if exact else "normal"))
    o.append(text(tx, yy + 19.0 + 6 * 4.0 + 2.6,
                  f"Paper also grows/shrinks with humidity — "
                  f"±{xlen * 0.002:.1f} mm over {xlen:.0f} is normal.",
                  size=2.5, color=GREY))
    return o, yy + max(ylen, 19.0 + 6 * 4.0 + 6.0) + 4.0


def layout_table(x, y, width, rows, heading):
    o = [text(x, y, heading, size=3.0, weight="bold")]
    o.append(line(x, y + 1.4, x + width, y + 1.4, w=0.2, color=GREY))
    yy = y + 5.4
    for label, val in rows:
        o.append(text(x, yy, label, size=2.7))
        o.append(text(x + width, yy, val, size=2.7, anchor="end",
                      family="Menlo, monospace"))
        yy += 4.0
    o.append(text(x, yy + 1.4,
                  "The paper is a convenience, not the datum — these numbers are. "
                  "If in doubt, mark them",
                  size=2.5, color=GREY))
    o.append(text(x, yy + 4.6,
                  "with a rule and a square straight onto the bar and centre-punch.",
                  size=2.5, color=GREY))
    return o, yy + 7.0


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------


def bar_outline(x, y, length, w, ch):
    """Flat bar with ch x ch chamfers on both corners of the left (pivot/rear) end."""
    return [(x + ch, y), (x + length, y), (x + length, y + w), (x + ch, y + w),
            (x, y + w - ch), (x, y + ch)]


def page_arm_bar(part, page_no, pages):
    o, y = header(part["title"], part["qty"], part["stock"], page_no, pages)
    L, W = part["length"], BAR_W
    bx = MARGIN + (PAGE_W - 2 * MARGIN - L) / 2.0
    by = y + 4.0

    o.append(poly(bar_outline(bx, by, L, W, CHAMFER), sw=0.4))
    o.append(centreline(bx - 3, bx + L + 3, by + W / 2))

    for hx, hd, _ in part["holes"]:
        o += hole(bx + hx, by + W / 2, hd)

    if part["slot"]:
        a, b, d = part["slot"]
        o += hole(bx + a, by + W / 2, d)
        o += hole(bx + b, by + W / 2, d)
        o.append(line(bx + a, by + W / 2 - d / 2, bx + b, by + W / 2 - d / 2,
                      w=0.3, color=RED))
        o.append(line(bx + a, by + W / 2 + d / 2, bx + b, by + W / 2 + d / 2,
                      w=0.3, color=RED))
        o.append(text(bx + (a + b) / 2, by + W / 2 - d / 2 - 1.8,
                      "saw + file: 25 slot", size=2.5, color=RED, anchor="middle"))

    # The 183.7 bar all but fills the sheet, so the width dimension goes INSIDE the
    # bar, in the clear stretch past the last hole — outside it would run off the edge.
    o += dim_v(by, by + W, bx + L - 6.0, f"{W:.0f}", backing=True)
    dy = by + W + 7.0
    o += dim_h(bx, bx + CHAMFER, dy, "10")
    o += dim_h(bx, bx + PIVOT_X, dy + 6.0, f"{PIVOT_X:.0f}")
    o += dim_h(bx, bx + BRACE_X, dy + 12.0, f"{BRACE_X:.1f}")
    last = part["slot"][0] if part["slot"] else part["holes"][-1][0]
    o += dim_h(bx, bx + last, dy + 18.0, f"{last:.1f}")
    if part["slot"]:
        o += dim_h(bx, bx + part["slot"][1], dy + 24.0, f"{part['slot'][1]:.1f}")
        o += dim_h(bx, bx + L, dy + 30.0, f"{L:.1f} overall")
        y = dy + 36.0
    else:
        o += dim_h(bx, bx + L, dy + 24.0, f"{L:.1f} overall")
        y = dy + 30.0

    o.append(text(bx, by - 2.2, "DATUM — chamfered (rear/pivot) end",
                  size=2.5, color=GREY))

    for i, n in enumerate(part["notes"]):
        o.append(text(MARGIN, y + i * 3.6, n, size=2.6))
    y += len(part["notes"]) * 3.6 + 3.0

    o2, y = scale_block(MARGIN, y, PAGE_W - 2 * MARGIN)
    o += o2

    rows = [("Overall length", f"{L:.1f}"),
            ("Bar width (stock)", f"{W:.1f}"),
            ("Centreline, from either edge", f"{W / 2:.1f}"),
            ("Chamfer, both rear corners", f"{CHAMFER:.0f} × {CHAMFER:.0f}")]
    for hx, hd, desc in part["holes"]:
        rows.append((f"{desc}, from datum", f"{hx:.1f}"))
    if part["slot"]:
        a, b, d = part["slot"]
        rows.append((f"Ø{d} slot, centres from datum", f"{a:.1f} → {b:.1f}"))
    o3, _ = layout_table(MARGIN, y + 2.0, PAGE_W - 2 * MARGIN, rows,
                         "HOLE LAYOUT (mm from the chamfered end, on the centreline)")
    o += o3
    return o


def page_carrier(page_no, pages):
    c = CARRIER
    o, y = header(c["title"], c["qty"], c["stock"], page_no, pages)
    # 220 mm of plate plus a header is most of the sheet: the width dimension goes
    # ABOVE the plate, because below it would fall off the bottom edge.
    bx, by = MARGIN + 4.0, y + 6.0
    W, H = c["w"], c["h"]

    o.append(rect(bx, by, W, H, sw=0.4))
    o.append(line(bx + W / 2, by - 1.5, bx + W / 2, by + H + 1.5,
                  w=0.15, color=GREY, dash="4 1.5 1 1.5"))

    fx, fy, fd = c["fork"]
    o += hole(bx + fx, by + fy, fd)
    ax, ay, ad, across = c["axle"]
    o += flatted_hole(bx + ax, by + ay, ad, across)
    px, py, pd = c["pivot"]
    o += hole(bx + px, by + py, pd)

    o += dim_v(by, by + fy, bx - 4.0, f"{fy:.0f}")
    o += dim_v(by + fy, by + ay, bx - 4.0, f"{ay - fy:.0f}")
    o += dim_v(by + ay, by + py, bx - 4.0, f"{py - ay:.0f}")
    o += dim_v(by, by + H, bx + W + 4.0, f"{H:.0f} overall")
    o += dim_h(bx, bx + W, by - 3.0, f"{W:.0f}")

    cx = bx + W + 16.0
    cw = PAGE_W - MARGIN - cx
    o.append(text(cx, by + 2.0, "Ø8.5 — M8 into the fork leg", size=2.7, color=RED))
    o.append(text(cx, by + 6.0, "Ø10.4 with two flats 8.9 apart:", size=2.7, color=RED))
    o.append(text(cx, by + 9.6, "the hub-axle torque-arm key. Drill", size=2.6))
    o.append(text(cx, by + 13.2, "Ø10.4, then file the two flats to", size=2.6))
    o.append(text(cx, by + 16.8, "8.9 across. No slot — a slot here", size=2.6))
    o.append(text(cx, by + 20.4, "lets the axle rotate.", size=2.6))
    o.append(text(cx, by + 26.0, "Ø16 pivot bore: drill 15.5 and", size=2.7, color=RED))
    o.append(text(cx, by + 29.6, "ream/file to a snug 16 — always as", size=2.6))
    o.append(text(cx, by + 33.2, "a clamped pair, so both carriers of", size=2.6))
    o.append(text(cx, by + 36.8, "a pod match.", size=2.6))

    o2, ny = scale_block(cx, by + 44.0, cw, xlen=100.0, ylen=50.0)
    o += o2

    rows = [("Overall length", f"{H:.0f}"),
            ("Strip width (stock)", f"{W:.0f}"),
            ("Ø8.5 fork bolt, from the near end", f"{fy:.0f}"),
            ("Ø10.4 axle key — above the fork bolt", f"{ay - fy:.0f}"),
            ("Ø16 pivot — below the axle key", f"{py - ay:.0f}"),
            ("All features on the centreline", f"{W / 2:.0f}")]
    o3, _ = layout_table(cx, ny + 4.0, cw, rows, "CARRIER LAYOUT (mm)")
    o += o3
    return o


def page_small(page_no, pages):
    o, y = header("CARRIER SMALL PARTS", "", "40 × 6 flat bar · offcuts",
                  page_no, pages)
    # 60 mm of row pitch put the first row's dimension chain into the second row's
    # heading — the tallest part here is 40 plus two dimension lines below it.
    slots = [(MARGIN + 4.0, y + 8.0), (MARGIN + 100.0, y + 8.0),
             (MARGIN + 4.0, y + 68.0), (MARGIN + 100.0, y + 68.0)]
    for part, (bx, by) in zip(SMALL, slots):
        o.append(text(bx, by - 4.6, f"{part['title']} {part['qty']}",
                      size=3.0, weight="bold"))
        o.append(text(bx, by - 1.4, part["note"], size=2.4, color=GREY))
        o.append(rect(bx, by, part["w"], part["h"], sw=0.4))
        if part["hole"]:
            hx, hy, hd = part["hole"]
            o += hole(bx + hx, by + hy, hd)
            o += dim_h(bx, bx + hx, by + part["h"] + 5.0, f"{hx:.1f}")
            o += dim_v(by, by + hy, bx - 4.0, f"{hy:.1f}")
        o += dim_h(bx, bx + part["w"], by + part["h"] + (11.0 if part["hole"] else 5.0),
                   f"{part['w']:g}")
        o += dim_v(by, by + part["h"], bx + part["w"] + 4.0, f"{part['h']:g}")

    y = y + 68.0 + 40.0 + 20.0
    o2, _ = scale_block(MARGIN, y, PAGE_W - 2 * MARGIN, xlen=150.0, ylen=40.0)
    o += o2
    return o


# ---------------------------------------------------------------------------
# assemble + render + verify
# ---------------------------------------------------------------------------


def build_html():
    builders = [lambda: page_arm_bar(TRAILING, 1, 4),
                lambda: page_arm_bar(LEADING, 2, 4),
                lambda: page_carrier(3, 4),
                lambda: page_small(4, 4)]
    pages = []
    for i, build in enumerate(builders, 1):
        _reset_extent()
        pages.append(build())
        if _max_y > PAGE_H - 2.0:
            raise SystemExit(
                f"page {i} overflows: lowest ink at {_max_y:.1f} mm, "
                f"page is {PAGE_H} mm (need <= {PAGE_H - 2.0:.1f})")
        print(f"  page {i}: lowest ink {_max_y:6.1f} mm of {PAGE_H} mm")
    parts = []
    for i, els in enumerate(pages):
        brk = "" if i == len(pages) - 1 else "page-break-after:always;"
        parts.append(
            f'<div class="pg" style="{brk}">'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}mm" '
            f'height="{PAGE_H}mm" viewBox="0 0 {PAGE_W} {PAGE_H}">'
            f'<rect width="{PAGE_W}" height="{PAGE_H}" fill="#fff"/>'
            + "".join(els) + "</svg></div>")
    return (
        "<!doctype html><meta charset='utf-8'>"
        "<title>Rev 011 — 1:1 drilling templates</title><style>"
        f"@page{{size:{PAGE_W}mm {PAGE_H}mm;margin:0}}"
        "html,body{margin:0;padding:0;background:#fff}"
        f".pg{{width:{PAGE_W}mm;height:{PAGE_H}mm;overflow:hidden}}"
        "svg{display:block}"
        "</style>" + "".join(parts))


def render():
    with open(HTML_OUT, "w") as f:
        f.write(build_html())
    if not os.path.exists(CHROME):
        sys.exit(f"Chrome not found at {CHROME} — cannot render the PDF.")
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
         f"--print-to-pdf={PDF_OUT}", HTML_OUT],
        check=True, capture_output=True)


# --- verification: re-measure the produced PDF, in PDF units -----------------

PT_PER_MM = 72.0 / 25.4


def _mul(a, b):
    return (a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5])


def _streams(data):
    out = []
    for m in re.finditer(rb"stream\r?\n", data):
        s = m.end()
        e = data.find(b"endstream", s)
        try:
            out.append(zlib.decompress(data[s:e]).decode("latin-1"))
        except Exception:
            pass
    return out


def _subpaths(content):
    """Yield (ctm, points) for every subpath, points in device pt."""
    toks = re.findall(r"/[^\s/\[\]<>()]+|[-+0-9.]+|[A-Za-z*'\"]+", content)
    ctm = (1, 0, 0, 1, 0, 0)
    stack, nums, sub, out = [], [], [], []

    def close():
        if len(sub) > 1:
            out.append((ctm, list(sub)))
        sub.clear()

    for t in toks:
        if re.fullmatch(r"[-+0-9.]+", t):
            try:
                nums.append(float(t))
            except ValueError:
                nums.append(0.0)
            continue
        if t == "q":
            stack.append(ctm)
        elif t == "Q":
            close()
            if stack:
                ctm = stack.pop()
        elif t == "cm" and len(nums) >= 6:
            close()
            ctm = _mul(tuple(nums[-6:]), ctm)
        elif t == "m" and len(nums) >= 2:
            close()
            sub.append((nums[-2], nums[-1]))
        elif t == "l" and len(nums) >= 2:
            sub.append((nums[-2], nums[-1]))
        elif t == "c" and len(nums) >= 6:
            for k in (0, 2, 4):
                sub.append((nums[-6 + k], nums[-6 + k + 1]))
        elif t == "re" and len(nums) >= 4:
            close()
            x, y, w, h = nums[-4:]
            sub.extend([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
            close()
        elif t in ("S", "s", "f", "f*", "F", "B", "B*", "b", "n"):
            close()
        nums.clear() if t not in ("q",) else None
    close()
    res = []
    for m, pts in out:
        res.append([(m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])
                    for x, y in pts])
    return res


def verify():
    data = open(PDF_OUT, "rb").read()
    boxes = re.findall(r"/MediaBox \[([-0-9. ]+)\]", data.decode("latin-1"))
    ok = True
    print(f"\n  {PDF_OUT}")
    print(f"  pages: {len(boxes)}")
    box_w, box_h = PAGE_W * PT_PER_MM, PAGE_H * PT_PER_MM
    for b in boxes[:1]:
        box_w, box_h = [float(v) for v in b.split()][2:]
        pw, ph = box_w / PT_PER_MM, box_h / PT_PER_MM
        good = abs(pw - PAGE_W) < 0.4 and abs(ph - PAGE_H) < 0.4
        ok &= good
        print(f"  page size: {pw:.2f} x {ph:.2f} mm "
              f"(want {PAGE_W} x {PAGE_H})  {'OK' if good else 'FAIL'}")

    spans = []
    outside = 0
    for content in _streams(data):
        for pts in _subpaths(content):
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            spans.append(((max(xs) - min(xs)) / PT_PER_MM,
                          (max(ys) - min(ys)) / PT_PER_MM, len(pts)))
            # anything drawn off the sheet means the layout overflowed; measured
            # against the real MediaBox, since Chrome rounds the page box a hair up
            tol = 0.5 * PT_PER_MM
            if (min(xs) < -tol or min(ys) < -tol
                    or max(xs) > box_w + tol or max(ys) > box_h + tol):
                outside += 1
    ok &= outside == 0
    print(f"  geometry off the sheet: {outside}  {'OK' if not outside else 'FAIL'}")

    # a chamfered bar is a 6-vertex polygon; Chrome may repeat the closing point
    expect = [("trailing bar outline", TRAILING["length"], BAR_W, (6, 7)),
              ("leading bar outline", LEADING["length"], BAR_W, (6, 7)),
              ("carrier outline", CARRIER["w"], CARRIER["h"], (4, 5)),
              ("tab stub outline", 55.0, 40.0, (4, 5)),
              ("brace web leading", 66.5, 30.0, (4, 5)),
              ("brace web trailing", 50.8, 30.0, (4, 5)),
              ("tensioner pusher block", 26.0, 14.0, (4, 5)),
              ("X ruler 150 mm", 150.0, 0.0, (2,)),
              ("X ruler 100 mm", 100.0, 0.0, (2,)),
              ("Y ruler 50 mm", 0.0, 50.0, (2,)),
              ("Y ruler 40 mm", 0.0, 40.0, (2,))]
    print("\n  measured back out of the rendered PDF:")
    for name, ew, eh, npts in expect:
        hit = None
        for w, h, n in spans:
            if n in npts and abs(w - ew) < 0.06 and abs(h - eh) < 0.06:
                hit = (w, h)
                break
        if hit:
            print(f"    OK    {name:24s} {hit[0]:8.3f} x {hit[1]:7.3f} mm")
        else:
            ok = False
            print(f"    FAIL  {name:24s} expected {ew:.2f} x {eh:.2f} mm — not found")
    # every drilled hole, by diameter, across all four pages
    found = []
    for content in _streams(data):
        for pts in _subpaths(content):
            if len(pts) < 12:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w = (max(xs) - min(xs)) / PT_PER_MM
            h = (max(ys) - min(ys)) / PT_PER_MM
            if w < 2.0 or abs(w - h) > 0.15:
                continue
            cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
            rr = [math.hypot(p[0] - cx, p[1] - cy) for p in pts]
            if max(rr) - min(rr) < 0.06 * max(rr):
                found.append(round((w + h) / 2, 2))
    want = sorted([D_PIVOT, D_BRACE, D_AXLE, D_AXLE,          # trailing bar
                   D_PIVOT, D_BRACE, D_AXLE,                  # leading bar
                   CARRIER["fork"][2], CARRIER["pivot"][2],    # carrier
                   SMALL[0]["hole"][2], SMALL[3]["hole"][2]])  # tab stub, lug
    got = sorted(found)
    holes_ok = len(got) == len(want) and all(
        abs(a - b) < 0.06 for a, b in zip(got, want))
    ok &= holes_ok
    print(f"\n  drilled holes: {len(got)} found, {len(want)} expected  "
          f"{'OK' if holes_ok else 'FAIL'}")
    print(f"    Ø expected: {[round(v, 1) for v in want]}")
    print(f"    Ø measured: {[round(v, 1) for v in got]}")

    # the carrier axle key: Ø10.4 circle cut by flats 8.9 apart (SCAD 641-642)
    ad, across = CARRIER["axle"][2], CARRIER["axle"][3]
    key_ok = False
    for content in _streams(data):
        for pts in _subpaths(content):
            if len(pts) < 12:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            w = (max(xs) - min(xs)) / PT_PER_MM
            h = (max(ys) - min(ys)) / PT_PER_MM
            if abs(w - ad) < 0.06 and abs(h - across) < 0.06:
                key_ok = True
    ok &= key_ok
    print(f"  carrier axle key Ø{ad} × {across} flats  "
          f"{'OK' if key_ok else 'FAIL'}")

    print("\n  " + ("ALL CHECKS PASSED — the sheet is true 1:1."
                    if ok else "*** VERIFICATION FAILED ***"))
    return ok


if __name__ == "__main__":
    render()
    sys.exit(0 if verify() else 1)
