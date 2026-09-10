#!/usr/bin/env python3
"""
Rev 012 — 1:1 printable templates for the rear-pod joint. Writes TWO files:

  rev012_green_plate_templates.pdf        A4 PORTRAIT, one whole part per page (3 pages)
      page 1  GREEN PLATE RIGHT (+z, rear shock eye)  — drawn top to bottom
      page 2  GREEN PLATE LEFT  (-z, front shock eye) — drawn top to bottom
      page 3  RAIL REAR END — the two sleeve holes (use it on all four rail walls)

  rev012_green_plate_templates_split.pdf  any paper (A4 or US Letter), 5 pages: each plate
      in two halves taped together on a JOIN LINE, plus the rail page

WHY TWO: A4 is 297 mm long, so a 260 mm plate fits on ONE A4 page when it runs top to
bottom (owner, 2026-09-10: "just fit it in top to bottom"). US Letter is only 279 mm, which
is why the paper-neutral 195 x 259.5 page of the Rev 011 templates has to split a plate.

Same method as make_1to1_templates.py (this script imports its drawing and PDF-measuring
code): every page is smaller than the printable area of its paper, so "Actual size" and
"Shrink oversized pages" both print 1:1; every page is one SVG whose unit is 1 mm; every
page has an X and a Y scale ruler; and the rendered PDF is measured back — outlines,
every hole's position and diameter, the axle keys and the rulers — before the script says
it is good.

GEOMETRY SOURCE: every number is read from apollo_track_pod_rev012.scad (the TEMPLATE_JSON
line echoed by render_mode="chassis_plates"), so the paper cannot drift from the model.

USAGE:  python3 make_rev012_templates.py
"""

import json
import math
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_1to1_templates as base  # noqa: E402  (drawing + PDF-measuring helpers)

SCAD = os.path.join(HERE, "apollo_track_pod_rev012.scad")
RED, GREY = base.RED, base.GREY
PT = base.PT_PER_MM
MARGIN = 5.0
OVERLAP = 10.0      # split file: each half runs this far past the join line
RAIL_L = 120.0      # length of rail drawn on the rail page

MODES = {
    # A4 portrait printable area is ~200 x 287 on common printers; stay inside it.
    "a4":    dict(w=200.0, h=275.0, pages=3, rulers=(80.0, 100.0, 150.0, 50.0),
                  html="rev012_green_plate_templates.html",
                  pdf="rev012_green_plate_templates.pdf",
                  paper="A4 PORTRAIT — the whole part is on this page. Check the ruler below BEFORE you drill."),
    # paper-neutral page of the Rev 011 templates (fits A4 and US Letter portrait)
    "split": dict(w=195.0, h=259.5, pages=5, rulers=(150.0, 50.0),
                  html="rev012_green_plate_templates_split.html",
                  pdf="rev012_green_plate_templates_split.pdf",
                  paper="A4 or US Letter both work — this page is smaller than either. "
                        "Check the ruler below BEFORE you cut or drill."),
}
PAGE_W, PAGE_H = MODES["a4"]["w"], MODES["a4"]["h"]   # set per mode in main()


# ---------------------------------------------------------------------------
# geometry — from the SCAD model
# ---------------------------------------------------------------------------

def geometry():
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "g.echo")
        subprocess.run(["openscad", "-o", out, "--export-format", "echo",
                        "-D", 'render_mode="chassis_plates"', SCAD],
                       check=True, capture_output=True)
        txt = open(out).read()
    m = re.search(r'TEMPLATE_JSON (\{.*?\})"', txt)
    if not m:
        sys.exit("TEMPLATE_JSON not found in the SCAD echo — is render_mode=\"chassis_plates\" intact?")
    return json.loads(m.group(1).replace('\\"', '"'))


def plate(G, side):
    """Holes as (from FRONT end, from TOP edge, diameter, kind, label)."""
    x0 = G["x0"]
    x1 = G["x1_right"] if side == "right" else G["x1_left"]
    top = G["yc"] + G["w"] / 2.0
    eye_x = G["eye_x"] if side == "right" else -G["eye_x"]
    holes = [
        (G["bolts"][0] - x0, top - G["yc"], G["bolt_hole"], "hole", "Ø13 — M12 into the rail"),
        (G["bolts"][1] - x0, top - G["yc"], G["bolt_hole"], "hole", "Ø13 — M12 into the rail"),
        (0.0 - x0, top - 0.0, G["key_d"], "key", "Ø10.4 key — hub axle"),
        (0.0 - x0, top - G["m8_y"], G["m8_hole"], "hole", "Ø8.4 — M8 to hub plate"),
        (eye_x - x0, top - G["eye_y"], G["eye_hole"], "hole", "Ø8.4 — shock top eye"),
    ]
    holes.sort(key=lambda h: h[0])
    L = x1 - x0
    return dict(side=side, L=L, W=G["w"], holes=holes, join=round(L / 2.0, 1),
                flats=G["key_flats"], title=f"GREEN PLATE {side.upper()}",
                eye="REAR shock eye · right side (+z)" if side == "right"
                    else "FRONT shock eye · left side (−z)")


def half_range(P, half):
    return (0.0, P["join"] + OVERLAP) if half == 1 else (P["join"] - OVERLAP, P["L"])


def half_holes(P, half):
    a, b = half_range(P, half)
    return [h for h in P["holes"] if a + h[2] / 2 + 0.5 <= h[0] <= b - h[2] / 2 - 0.5]


def rail_holes(G):
    return [(G["rail_end_x"] - G["bolts"][1], G["rail_h"] - G["rail_hole_up"], G["sleeve_od"]),
            (G["rail_end_x"] - G["bolts"][0], G["rail_h"] - G["rail_hole_up"], G["sleeve_od"])]


# ---------------------------------------------------------------------------
# shared furniture
# ---------------------------------------------------------------------------

def header(title, stock, paper_line, page_no, pages):
    o = [base.text(MARGIN, MARGIN + 3.4, f"REV 012 · 1:1 TEMPLATE — {title}", size=4.0, weight="bold"),
         base.text(PAGE_W - MARGIN, MARGIN + 3.4, f"{page_no}/{pages}", size=3.0, color=GREY, anchor="end"),
         base.text(MARGIN, MARGIN + 7.6, stock, size=2.8, color=GREY),
         base.line(MARGIN, MARGIN + 9.4, PAGE_W - MARGIN, MARGIN + 9.4, w=0.3)]
    y = MARGIN + 11.2
    o.append(base.rect(MARGIN, y, PAGE_W - 2 * MARGIN, 9.6, sw=0.35, color=RED))
    o.append(base.text(MARGIN + 2.0, y + 3.9,
                       "PRINT AT 100% / “ACTUAL SIZE” — NOT “Fit to page”, NOT “Shrink oversized pages”.",
                       size=3.1, weight="bold", color=RED))
    o.append(base.text(MARGIN + 2.0, y + 7.9, paper_line, size=2.7, color=RED))
    return o, y + 12.4


def draw_hole(P, cx, cy, dia, kind, rotated=False):
    if kind != "key":
        return base.hole(cx, cy, dia)
    els = base.flatted_hole(cx, cy, dia, P["flats"])
    if not rotated:
        return els
    # plate drawn top to bottom: the flats stay parallel to the bar's long edges
    return [f'<g transform="rotate(90 {cx:.3f} {cy:.3f})">' + "".join(els) + "</g>"]


def rail_drawing(G, bx, by, RH):
    o = [base.rect(bx, by, RAIL_L, RH, sw=0.4),
         base.text(bx, by - 1.6, "REAR END of the rail (datum) — beside the rear pod", size=2.5, color=GREY),
         base.text(bx + RAIL_L - 1.0, by + RH - 1.6, "BOTTOM EDGE", size=2.4, color=GREY, anchor="end")]
    holes = rail_holes(G)
    for d, yt, dia in holes:
        o += base.hole(bx + d, by + yt, dia)
    up = RH - holes[0][1]
    o += base.dim_h(bx, bx + holes[0][0], by + RH + 6.0, f"{holes[0][0]:g}")
    o += base.dim_h(bx, bx + holes[1][0], by + RH + 11.5, f"{holes[1][0]:g}")
    o += base.dim_v(by + holes[0][1], by + RH, bx - 5.0, f"{up:g} up")
    o += base.dim_v(by, by + holes[0][1], bx + RAIL_L + 5.0, f"{holes[0][1]:g}")
    o += base.dim_v(by, by + RH, bx - 12.0, f"{RH:g}")
    return o


# ---------------------------------------------------------------------------
# A4 portrait: a whole green plate, top to bottom
# ---------------------------------------------------------------------------

def page_plate_a4(P, page_no, pages):
    L, W = P["L"], P["W"]
    bx, by = 41.0, 11.0                  # plate: across the page = up from the BOTTOM edge
    o = [base.rect(bx, by, W, L, sw=0.4),
         base.line(bx + W / 2, by - 1.5, bx + W / 2, by + L + 1.5, w=0.15, color=GREY, dash="4 1.5 1 1.5"),
         base.text(bx + W / 2, by + 5.5, "FRONT END (datum)", size=2.4, color=GREY, anchor="middle"),
         base.text(bx + W / 2, by + L - 2.5, "REAR END", size=2.4, color=GREY, anchor="middle"),
         f'<g transform="rotate(-90 {bx + 3.4:.3f} {by + L / 2:.3f})">'
         + base.text(bx + 3.4, by + L / 2, "BOTTOM EDGE of the bar", size=2.3, color=GREY, anchor="middle")
         + "</g>"]
    for d, yt, dia, kind, _ in P["holes"]:
        u = W - yt
        cx, cy = bx + u, by + d
        o += draw_hole(P, cx, cy, dia, kind, rotated=True)
        o.append(base.text(cx, cy + dia / 2 + 5.8, f"{u:.1f} up", size=2.3, color=RED, anchor="middle"))

    col, done = 0, []
    for d, _, _, _, _ in P["holes"]:
        if any(abs(d - q) < 0.05 for q in done):
            continue
        done.append(d)
        x = bx - 4.0 - col * 6.0
        o.append(base.line(x + 1.6, by + d, bx, by + d, w=0.12, color=GREY, dash="1 1"))
        o += base.dim_v(by, by + d, x, f"{d:.1f}", backing=True)
        col += 1
    o += base.dim_v(by, by + L, bx - 4.0 - col * 6.0, f"{L:g} overall", backing=True)
    o += base.dim_h(bx, bx + W, by - 4.5, f"{W:g}")

    # ---- right-hand column: title, print warning, how-to, holes, rulers
    x0 = bx + W + 12.0
    cw = PAGE_W - MARGIN - x0
    o.append(base.text(PAGE_W - MARGIN, 8.4, f"{page_no}/{pages}", size=3.0, color=GREY, anchor="end"))
    o.append(base.text(x0, 9.0, "REV 012 · 1:1 TEMPLATE", size=3.4, weight="bold"))
    o.append(base.text(x0, 15.2, f"{P['title']} ×1", size=4.4, weight="bold"))
    o.append(base.text(x0, 20.2, f"60 × 6 flat bar · {L:g} long · no cut", size=2.7, color=GREY))
    o.append(base.text(x0, 24.2, P["eye"], size=2.7, color=GREY))
    o.append(base.rect(x0, 28.0, cw, 17.5, sw=0.35, color=RED))
    o.append(base.text(x0 + 2.0, 33.0, "PRINT AT 100% / “ACTUAL SIZE”", size=3.1, weight="bold", color=RED))
    o.append(base.text(x0 + 2.0, 37.6, "NOT “Fit to page”, NOT “Shrink oversized pages”.", size=2.6, color=RED))
    o.append(base.text(x0 + 2.0, 42.2, "A4 PORTRAIT — the whole plate is on this page.", size=2.6, color=RED))

    notes = ["HOW TO USE",
             "1. Cut the paper out on the outline.",
             "2. Lay it on the bar, long edges on the bar edges,",
             "   FRONT END at the end that bolts to the rail.",
             "3. Tape. Punch every red cross. Drill.",
             "“up” = mm from the BOTTOM edge of the bar",
             "(the left edge in this drawing).",
             "Key: drill Ø10.4, file two flats 8.9 apart,",
             "parallel to the bar edges. No slot.",
             "Rear-pod HUB PLATE: drill Ø8.4 at 44 mm from",
             "its top end. Bolt + key, then weld all round."]
    for i, n in enumerate(notes):
        o.append(base.text(x0, 53.0 + i * 4.1, n, size=2.6, weight="bold" if i == 0 else "normal"))
    y = 53.0 + len(notes) * 4.1 + 4.0
    o.append(base.text(x0, y, "HOLES (from the front end · up)", size=2.8, weight="bold"))
    o.append(base.line(x0, y + 1.4, x0 + cw, y + 1.4, w=0.2, color=GREY))
    for i, (d, yt, _, _, lab) in enumerate(P["holes"]):
        o.append(base.text(x0, y + 5.4 + i * 4.0, lab, size=2.6))
        o.append(base.text(x0 + cw, y + 5.4 + i * 4.0, f"{d:.1f} · {W - yt:.1f} up", size=2.6,
                           anchor="end", family="Menlo, monospace"))
    y += 5.4 + len(P["holes"]) * 4.0 + 8.0

    xl, yl = MODES["a4"]["rulers"][0], MODES["a4"]["rulers"][1]
    o += base.ruler_h(x0, y + 8.0, xl, f"SCALE CHECK — exactly {xl:.0f} mm")
    yy = y + 20.0
    o += base.ruler_v(x0 + 6.0, yy, yl, f"and this {yl:.0f} mm")
    tx = x0 + 24.0
    o.append(base.text(tx, yy + 3.0, "Wrong? Do not drill.", size=2.7, weight="bold"))
    o.append(base.text(tx, yy + 7.0, f"Reprint % = {xl * 100:.0f} ÷ measured", size=2.6))
    o.append(base.text(tx, yy + 12.5, f"if {xl:.0f} reads…   reprint at", size=2.4, color=GREY, weight="bold"))
    for i, frac in enumerate((0.94, 0.96, 0.98, 1.00, 1.02, 1.04)):
        ry = yy + 17.0 + i * 4.2
        exact = frac == 1.00
        o.append(base.text(tx, ry, f"{xl * frac:.1f} mm", size=2.6))
        o.append(base.text(tx + 24.0, ry, "correct — go" if exact else f"{100 / frac:.0f}%",
                           size=2.6, weight="bold" if exact else "normal"))
    return o


def page_rail(G, page_no, pages, paper_line):
    o, y = header("RAIL REAR END · 2 SLEEVE HOLES",
                  "100 × 40 × 2 tube · use on BOTH walls of BOTH rails (4 times)", paper_line, page_no, pages)
    RH = G["rail_h"]
    bx, by = MARGIN + 30.0, y + 12.0
    o += rail_drawing(G, bx, by, RH)
    y = by + RH + 20.0
    notes = ["Line up the REAR END and the BOTTOM EDGE every time — the holes are not in the middle.",
             "Best: drill a Ø6 pilot straight through both walls on a drill press, then open each side",
             f"to Ø{G['sleeve_od']:g} with a hole saw. Weld a Ø{G['sleeve_od']:g} × Ø13 × 40 steel sleeve "
             "into each pair of holes,",
             "flush with both walls. The M12 goes in from OUTSIDE, through the sleeve and the green plate,",
             "into the M12 nut welded on the green plate."]
    for i, n in enumerate(notes):
        o.append(base.text(MARGIN, y + i * 3.6, n, size=2.6))
    y += len(notes) * 3.6 + 3.0
    o2, _ = base.scale_block(MARGIN, y, PAGE_W - 2 * MARGIN, xlen=150.0, ylen=50.0)
    return o + o2


# ---------------------------------------------------------------------------
# split pages (any paper) — each plate in two halves
# ---------------------------------------------------------------------------

def table(x, y, width, rows, heading):
    o = [base.text(x, y, heading, size=3.0, weight="bold"),
         base.line(x, y + 1.4, x + width, y + 1.4, w=0.2, color=GREY)]
    yy = y + 5.2
    for label, val in rows:
        o.append(base.text(x, yy, label, size=2.7))
        o.append(base.text(x + width, yy, val, size=2.7, anchor="end", family="Menlo, monospace"))
        yy += 3.9
    o.append(base.text(x, yy + 1.0, "The paper is a guide; these numbers are the datum — "
                                    "check them with a steel rule before you drill.", size=2.5, color=GREY))
    return o, yy + 4.0


def page_half(P, half, page_no, pages):
    L, W, join = P["L"], P["W"], P["join"]
    a, b = half_range(P, half)
    span = b - a
    o, y = header(f"{P['title']} · HALF {half} OF 2",
                  f"60 × 6 flat bar · plate {L:g} long · {P['eye']} · no cut, holes only",
                  MODES["split"]["paper"], page_no, pages)
    bx = MARGIN + 22.0 + (PAGE_W - 2 * MARGIN - 22.0 - 10.0 - span) / 2.0
    by = y + 11.0
    o.append(base.rect(bx, by, span, W, sw=0.4))
    o.append(base.centreline(bx - 2.0, bx + span + 2.0, by + W / 2.0))
    jx = bx + (join - a)
    o.append(base.line(jx, by - 5.0, jx, by + W + 3.0, w=0.5, color=RED, dash="3 1.2"))
    o.append(base.text(jx, by - 6.3, f"JOIN LINE · {join:g} from the front end",
                       size=2.6, color=RED, anchor="middle", weight="bold"))
    if half == 1:
        o.append(base.text(bx, by - 1.6, "FRONT END (datum) — towards the frame", size=2.4, color=GREY))
    else:
        o.append(base.text(bx + span, by - 1.6, "REAR END — past the hub axle", size=2.4, color=GREY, anchor="end"))
    shown = half_holes(P, half)
    for d, yt, dia, kind, _ in shown:
        o += draw_hole(P, bx + (d - a), by + yt, dia, kind)
    ref_x, ref_d = (bx, 0.0) if half == 1 else (jx, join)
    dy, row, done = by + W + 7.0, 0, []
    for d, _, _, _, _ in shown:
        if any(abs(d - q) < 0.05 for q in done):
            continue
        done.append(d)
        o += base.dim_h(ref_x, bx + (d - a), dy + row * 6.0, f"{abs(d - ref_d):.1f}")
        row += 1
    if half == 2:
        o += base.dim_h(jx, bx + span, dy + row * 6.0, f"{L - join:.1f} to the rear end")
        row += 1
    col, done = 0, []
    for d, yt, _, _, _ in shown:
        if any(abs(yt - q) < 0.05 for q in done):
            continue
        done.append(yt)
        x = bx - 4.0 - col * 6.0
        o.append(base.line(x + 1.6, by + yt, bx + (d - a), by + yt, w=0.12, color=GREY, dash="1 1"))
        o += base.dim_v(by + yt, by + W, x, f"{W - yt:.1f}")
        col += 1
    o += base.dim_v(by, by + W, bx + span + 4.0, f"{W:g}")
    y = dy + row * 6.0 + 1.5
    notes = (["Cut BOTH halves out on the outline. Lay them on the bar, long edges on the bar edges,",
              f"join lines on top of each other ({2 * OVERLAP:g} mm overlap). Tape. Punch every red cross.",
              "This half = the FRONT end: the 2 × Ø13 holes for the M12 bolts into the rail."]
             if half == 1 else
             ["This half = the REAR end: hub-axle key, M8 hole and the shock top eye.",
              "Key: drill Ø10.4, then file two flats 8.9 apart (top and bottom). No slot.",
              "Match the rear-pod HUB PLATE: drill Ø8.4 at 44 mm from its top end (between the",
              "fork hole and the key). Bolt + key the plate, then weld it to the hub plate all round."])
    for i, n in enumerate(notes):
        o.append(base.text(MARGIN, y + i * 3.6, n, size=2.6))
    y += len(notes) * 3.6 + 2.0
    o2, y = base.scale_block(MARGIN, y, PAGE_W - 2 * MARGIN, xlen=150.0, ylen=50.0)
    o += o2
    rows = [(f"{lab}", f"{d:.1f} from front · {W - yt:.1f} up") for d, yt, _, _, lab in P["holes"]]
    o3, _ = table(MARGIN, y + 1.0, PAGE_W - 2 * MARGIN, rows,
                  "ALL HOLES OF THIS PLATE (mm from the front end · up from the bottom edge)")
    return o + o3


# ---------------------------------------------------------------------------
# assemble, render, verify
# ---------------------------------------------------------------------------

def builders(mode, G, R, Lp):
    if mode == "a4":
        return [lambda: page_plate_a4(R, 1, 3), lambda: page_plate_a4(Lp, 2, 3),
                lambda: page_rail(G, 3, 3, MODES["a4"]["paper"])]
    return [lambda: page_half(R, 1, 1, 5), lambda: page_half(R, 2, 2, 5),
            lambda: page_half(Lp, 1, 3, 5), lambda: page_half(Lp, 2, 4, 5),
            lambda: page_rail(G, 5, 5, MODES["split"]["paper"])]


def expectations(mode, G, R, Lp):
    """(name, outline w, outline h, sorted holes (from left, from top, Ø; 10.4 = the key))."""
    def dia(h):
        return h[2] if h[3] == "hole" else 10.4
    exp = []
    for P in (R, Lp):
        if mode == "a4":        # top to bottom: from left = up from the bottom edge, from top = along
            exp.append((P["title"], P["W"], P["L"],
                        sorted((round(P["W"] - h[1], 1), round(h[0], 1), dia(h)) for h in P["holes"])))
        else:
            for half in (1, 2):
                a, b = half_range(P, half)
                exp.append((f"{P['title']} half {half}", b - a, P["W"],
                            sorted((round(h[0] - a, 1), round(h[1], 1), dia(h)) for h in half_holes(P, half))))
    exp.append(("rail rear end", RAIL_L, G["rail_h"],
                sorted((round(d, 1), round(yt, 1), dd) for d, yt, dd in rail_holes(G))))
    return exp


def build_html(mode, G, R, Lp):
    pages = []
    for i, build in enumerate(builders(mode, G, R, Lp), 1):
        base._reset_extent()
        pages.append(build())
        if base._max_y > PAGE_H - 2.0:
            raise SystemExit(f"[{mode}] page {i} overflows: lowest ink at {base._max_y:.1f} mm "
                             f"(need <= {PAGE_H - 2.0:.1f})")
        print(f"  [{mode}] page {i}: lowest ink {base._max_y:6.1f} mm of {PAGE_H} mm")
    parts = []
    for i, els in enumerate(pages):
        brk = "" if i == len(pages) - 1 else "page-break-after:always;"
        parts.append(f'<div class="pg" style="{brk}"><svg xmlns="http://www.w3.org/2000/svg" '
                     f'width="{PAGE_W}mm" height="{PAGE_H}mm" viewBox="0 0 {PAGE_W} {PAGE_H}">'
                     f'<rect width="{PAGE_W}" height="{PAGE_H}" fill="#fff"/>' + "".join(els) + "</svg></div>")
    return ("<!doctype html><meta charset='utf-8'><title>Rev 012 — green plate templates</title><style>"
            f"@page{{size:{PAGE_W}mm {PAGE_H}mm;margin:0}}html,body{{margin:0;padding:0;background:#fff}}"
            f".pg{{width:{PAGE_W}mm;height:{PAGE_H}mm;overflow:hidden}}svg{{display:block}}</style>"
            + "".join(parts))


def render(mode, G, R, Lp):
    html, pdf = os.path.join(HERE, MODES[mode]["html"]), os.path.join(HERE, MODES[mode]["pdf"])
    with open(html, "w") as f:
        f.write(build_html(mode, G, R, Lp))
    if not os.path.exists(base.CHROME):
        sys.exit(f"Chrome not found at {base.CHROME} — cannot render the PDF.")
    subprocess.run([base.CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
                    f"--print-to-pdf={pdf}", html], check=True, capture_output=True)
    return pdf


def _shapes(content):
    rects, circles, keys, rulers, pts_all = [], [], [], [], []
    for pts in base._subpaths(content):
        pts_all.append(pts)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        w, h = (max(xs) - min(xs)) / PT, (max(ys) - min(ys)) / PT
        box = (min(xs), min(ys), max(xs), max(ys))
        if len(pts) in (4, 5) and w > 20 and h > 20:
            rects.append((w, h, box))
        elif len(pts) == 2:
            rulers.append((w, h))
        elif len(pts) >= 12 and min(w, h) >= 2.0:
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            if abs(w - h) <= 0.15:
                rr = [math.hypot(p[0] - cx, p[1] - cy) for p in pts]
                if max(rr) - min(rr) < 0.06 * max(rr):
                    circles.append(((w + h) / 2, cx, cy))
            elif {round(w, 1), round(h, 1)} <= {10.3, 10.4, 10.5, 8.8, 8.9, 9.0} and abs(abs(w - h) - 1.5) < 0.1:
                keys.append((10.4, cx, cy))       # flatted key, either orientation
    return rects, circles, keys, rulers, pts_all


def verify(mode, pdf, G, R, Lp):
    data = open(pdf, "rb").read()
    ok = True
    boxes = re.findall(r"/MediaBox \[([-0-9. ]+)\]", data.decode("latin-1"))
    want_pages = MODES[mode]["pages"]
    print(f"\n  {pdf}\n  pages: {len(boxes)} (want {want_pages})")
    ok &= len(boxes) == want_pages
    bw, bh = [float(v) for v in boxes[0].split()][2:]
    good = abs(bw / PT - PAGE_W) < 0.4 and abs(bh / PT - PAGE_H) < 0.4
    ok &= good
    print(f"  page size: {bw / PT:.2f} x {bh / PT:.2f} mm (want {PAGE_W:g} x {PAGE_H:g})  {'OK' if good else 'FAIL'}")

    found, rulers, n_circ, n_keys, outside = [], [], 0, 0, 0
    tol = 0.5 * PT
    for content in base._streams(data):
        rects, circles, keys, rl, pts_all = _shapes(content)
        rulers += rl
        n_circ += len(circles)
        n_keys += len(keys)
        for pts in pts_all:
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            if min(xs) < -tol or min(ys) < -tol or max(xs) > bw + tol or max(ys) > bh + tol:
                outside += 1
        for w, h, box in rects:
            inside = sorted((round((cx - box[0]) / PT, 1), round((box[3] - cy) / PT, 1), round(d, 1))
                            for d, cx, cy in circles + keys
                            if box[0] < cx < box[2] and box[1] < cy < box[3])
            found.append((w, h, inside))
    ok &= outside == 0
    print(f"  geometry off the sheet: {outside}  {'OK' if outside == 0 else 'FAIL'}")

    print("  measured back out of the PDF (outline, then holes: from left · from top · Ø):")
    used = Counter()
    exp = expectations(mode, G, R, Lp)
    for name, ew, eh, holes in exp:
        hit = None
        for i, (w, h, inside) in enumerate(found):
            if used[i] or abs(w - ew) > 0.06 or abs(h - eh) > 0.06 or len(inside) != len(holes):
                continue
            if all(abs(p[0] - q[0]) <= 0.15 and abs(p[1] - q[1]) <= 0.15 and abs(p[2] - q[2]) <= 0.1
                   for p, q in zip(inside, holes)):
                hit = i
                break
        if hit is None:
            ok = False
            print(f"    FAIL  {name:26s} {ew:.1f} x {eh:.1f} with {holes} — not found")
        else:
            used[hit] += 1
            print(f"    OK    {name:26s} {found[hit][0]:7.2f} x {found[hit][1]:6.2f}  holes {found[hit][2]}")
    for L in MODES[mode]["rulers"]:
        r_ok = any(abs(w - L) < 0.06 or abs(h - L) < 0.06 for w, h in rulers)
        ok &= r_ok
        print(f"    {'OK  ' if r_ok else 'FAIL'}  scale ruler {L:g} mm")
    want_c = sum(1 for _, _, _, hs in exp for h in hs if abs(h[2] - 10.4) > 0.01)
    c_ok, k_ok = n_circ == want_c, n_keys == 2
    ok &= c_ok and k_ok
    print(f"    {'OK  ' if c_ok else 'FAIL'}  round holes: {n_circ} (want {want_c})")
    print(f"    {'OK  ' if k_ok else 'FAIL'}  axle keys Ø10.4 x 8.9: {n_keys} (want 2)")
    print("  " + ("ALL CHECKS PASSED — true 1:1 and matches the model." if ok else "*** VERIFICATION FAILED ***"))
    return ok


if __name__ == "__main__":
    G = geometry()
    print("  geometry from the SCAD:", G)
    R, Lp = plate(G, "right"), plate(G, "left")
    all_ok = True
    for mode in ("a4", "split"):
        PAGE_W, PAGE_H = MODES[mode]["w"], MODES[mode]["h"]
        pdf = render(mode, G, R, Lp)
        all_ok &= verify(mode, pdf, G, R, Lp)
    sys.exit(0 if all_ok else 1)
