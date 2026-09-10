#!/usr/bin/env python3
"""
Rev 012 — 1:1 printable templates for the rear-pod joint (rev012_green_plate_templates.pdf).

    page 1-2  GREEN PLATE RIGHT (+z, rear shock eye)  — 60 x 6, in two halves
    page 3-4  GREEN PLATE LEFT  (-z, front shock eye) — 60 x 6, in two halves
    page 5    RAIL REAR END — the two sleeve holes (use it on all four rail walls)

Same method as make_1to1_templates.py (this script imports its drawing, scale-check and
PDF-measuring code): the page is smaller than the printable area of both A4 and Letter,
every page is one SVG whose unit is 1 mm, each page has X and Y scale checks, and the
rendered PDF is measured back before the script says it is good.

A green plate (up to 260 mm) is longer than the page, so it is split at a JOIN LINE. Each
half runs OVERLAP mm past the line: cut both halves out, lay them on the bar with the
long edges on the bar edges, put the join lines on top of each other, tape, then punch.

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
import make_1to1_templates as base  # noqa: E402  (drawing + verification helpers)

SCAD = os.path.join(HERE, "apollo_track_pod_rev012.scad")
HTML_OUT = os.path.join(HERE, "rev012_green_plate_templates.html")
PDF_OUT = os.path.join(HERE, "rev012_green_plate_templates.pdf")
PAGE_W, PAGE_H, MARGIN = base.PAGE_W, base.PAGE_H, base.MARGIN
RED, GREY = base.RED, base.GREY
PT = base.PT_PER_MM
OVERLAP = 10.0      # each half runs this far past the join line (20 mm of paper overlap)
RAIL_L = 120.0      # length of rail drawn on the rail page


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
        (0.0 - x0, top - 0.0, G["key_d"], "key", "Ø10.4 key, flats 8.9 — hub axle"),
        (0.0 - x0, top - G["m8_y"], G["m8_hole"], "hole", "Ø8.4 — M8 to the hub plate"),
        (eye_x - x0, top - G["eye_y"], G["eye_hole"], "hole", "Ø8.4 — shock top eye"),
    ]
    holes.sort(key=lambda h: h[0])
    L = x1 - x0
    return dict(side=side, L=L, W=G["w"], holes=holes, join=round(L / 2.0, 1),
                flats=G["key_flats"],
                title=f"GREEN PLATE {side.upper()}",
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
# pages
# ---------------------------------------------------------------------------

def header(title, stock, page_no, pages):
    o = [base.text(MARGIN, MARGIN + 3.4, f"REV 012 · 1:1 TEMPLATE — {title}", size=4.0, weight="bold"),
         base.text(PAGE_W - MARGIN, MARGIN + 3.4, f"{page_no}/{pages}", size=3.0, color=GREY, anchor="end"),
         base.text(MARGIN, MARGIN + 7.6, stock, size=2.8, color=GREY),
         base.line(MARGIN, MARGIN + 9.4, PAGE_W - MARGIN, MARGIN + 9.4, w=0.3)]
    y = MARGIN + 11.2
    o.append(base.rect(MARGIN, y, PAGE_W - 2 * MARGIN, 9.6, sw=0.35, color=RED))
    o.append(base.text(MARGIN + 2.0, y + 3.9,
                       "PRINT AT 100% / “ACTUAL SIZE” — NOT “Fit to page”, NOT “Shrink oversized pages”.",
                       size=3.1, weight="bold", color=RED))
    o.append(base.text(MARGIN + 2.0, y + 7.9,
                       "A4 or US Letter both work — this page is smaller than either. "
                       "Check the ruler below BEFORE you cut or drill.", size=2.7, color=RED))
    return o, y + 12.4


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
                  page_no, pages)
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
        o.append(base.text(bx + span, by - 1.6, "REAR END — past the hub axle", size=2.4,
                           color=GREY, anchor="end"))

    shown = half_holes(P, half)
    for d, yt, dia, kind, _ in shown:
        cx, cy = bx + (d - a), by + yt
        o += base.flatted_hole(cx, cy, dia, P["flats"]) if kind == "key" else base.hole(cx, cy, dia)

    # horizontal dimensions: from the front end (half 1) or from the join line (half 2)
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

    # vertical dimensions: from the BOTTOM edge, one column per height
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
    notes = ([f"Cut BOTH halves out on the outline. Lay them on the bar, long edges on the bar edges,",
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
                  f"ALL HOLES OF THIS PLATE (mm from the front end · up from the bottom edge)")
    o += o3
    return o


def page_rail(G, page_no, pages):
    o, y = header("RAIL REAR END · 2 SLEEVE HOLES",
                  "100 × 40 × 2 tube · use on BOTH walls of BOTH rails (4 times)", page_no, pages)
    RH = G["rail_h"]
    bx, by = MARGIN + 30.0, y + 12.0
    o.append(base.rect(bx, by, RAIL_L, RH, sw=0.4))
    o.append(base.text(bx, by - 1.6, "REAR END of the rail (datum) — the end beside the rear pod",
                       size=2.5, color=GREY))
    o.append(base.text(bx + RAIL_L - 1.0, by + RH - 1.6, "BOTTOM EDGE", size=2.4, color=GREY, anchor="end"))
    holes = rail_holes(G)
    for d, yt, dia in holes:
        o += base.hole(bx + d, by + yt, dia)
    up = RH - holes[0][1]
    o += base.dim_h(bx, bx + holes[0][0], by + RH + 7.0, f"{holes[0][0]:g}")
    o += base.dim_h(bx, bx + holes[1][0], by + RH + 13.0, f"{holes[1][0]:g}")
    o += base.dim_v(by + holes[0][1], by + RH, bx - 5.0, f"{up:g} up from the bottom")
    o += base.dim_v(by, by + holes[0][1], bx + RAIL_L + 5.0, f"{holes[0][1]:g}")
    o += base.dim_v(by, by + RH, bx - 12.0, f"{RH:g}")

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
    o += o2
    return o


# ---------------------------------------------------------------------------
# assemble, render, verify
# ---------------------------------------------------------------------------

def build_html(G, R, Lp):
    builders = [lambda: page_half(R, 1, 1, 5), lambda: page_half(R, 2, 2, 5),
                lambda: page_half(Lp, 1, 3, 5), lambda: page_half(Lp, 2, 4, 5),
                lambda: page_rail(G, 5, 5)]
    pages = []
    for i, build in enumerate(builders, 1):
        base._reset_extent()
        pages.append(build())
        if base._max_y > PAGE_H - 2.0:
            raise SystemExit(f"page {i} overflows: lowest ink at {base._max_y:.1f} mm "
                             f"(need <= {PAGE_H - 2.0:.1f})")
        print(f"  page {i}: lowest ink {base._max_y:6.1f} mm of {PAGE_H} mm")
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


def render(G, R, Lp):
    with open(HTML_OUT, "w") as f:
        f.write(build_html(G, R, Lp))
    if not os.path.exists(base.CHROME):
        sys.exit(f"Chrome not found at {base.CHROME} — cannot render the PDF.")
    subprocess.run([base.CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=4000",
                    f"--print-to-pdf={PDF_OUT}", HTML_OUT], check=True, capture_output=True)


def _shapes(content):
    rects, circles, keys, rulers = [], [], [], []
    for pts in base._subpaths(content):
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        w, h = (max(xs) - min(xs)) / PT, (max(ys) - min(ys)) / PT
        box = (min(xs), min(ys), max(xs), max(ys))
        if len(pts) in (4, 5) and w > 20 and h > 20:
            rects.append((w, h, box))
        elif len(pts) == 2:
            rulers.append((w, h))
        elif len(pts) >= 12 and w >= 2.0:
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            if abs(w - h) <= 0.15:
                rr = [math.hypot(p[0] - cx, p[1] - cy) for p in pts]
                if max(rr) - min(rr) < 0.06 * max(rr):
                    circles.append(((w + h) / 2, cx, cy))
            elif abs(w - 10.4) < 0.08 and abs(h - 8.9) < 0.08:
                keys.append((10.4, cx, cy))
    return rects, circles, keys, rulers


def verify(G, R, Lp):
    data = open(PDF_OUT, "rb").read()
    ok = True
    boxes = re.findall(r"/MediaBox \[([-0-9. ]+)\]", data.decode("latin-1"))
    print(f"\n  {PDF_OUT}\n  pages: {len(boxes)} (want 5)")
    ok &= len(boxes) == 5
    bw, bh = [float(v) for v in boxes[0].split()][2:]
    good = abs(bw / PT - PAGE_W) < 0.4 and abs(bh / PT - PAGE_H) < 0.4
    ok &= good
    print(f"  page size: {bw / PT:.2f} x {bh / PT:.2f} mm  {'OK' if good else 'FAIL'}")

    # expected outlines and, inside each, the holes at their positions (from left edge, from top edge)
    expect = []
    for P in (R, Lp):
        for half in (1, 2):
            a, b = half_range(P, half)
            exp = sorted((round(d - a, 1), round(yt, 1), dia if kind == "hole" else 10.4)
                         for d, yt, dia, kind, _ in half_holes(P, half))
            expect.append((f"{P['title']} half {half}", b - a, P["W"], exp))
    expect.append(("rail rear end", RAIL_L, G["rail_h"],
                   sorted((round(d, 1), round(yt, 1), dia) for d, yt, dia in rail_holes(G))))

    found_outlines, all_rulers, n_circ, n_keys = [], [], 0, 0
    for content in base._streams(data):
        rects, circles, keys, rulers = _shapes(content)
        all_rulers += rulers
        n_circ += len(circles)
        n_keys += len(keys)
        for w, h, box in rects:
            inside = sorted((round((cx - box[0]) / PT, 1), round((box[3] - cy) / PT, 1), round(d, 1))
                            for d, cx, cy in circles + keys
                            if box[0] < cx < box[2] and box[1] < cy < box[3])
            found_outlines.append((w, h, inside))

    print("\n  measured back out of the rendered PDF (outline, then holes: from left · from top · Ø):")
    used = Counter()
    for name, ew, eh, exp in expect:
        hit = None
        for i, (w, h, inside) in enumerate(found_outlines):
            if used[i] or abs(w - ew) > 0.06 or abs(h - eh) > 0.06 or len(inside) != len(exp):
                continue
            if all(abs(p[0] - q[0]) <= 0.15 and abs(p[1] - q[1]) <= 0.15 and abs(p[2] - q[2]) <= 0.1
                   for p, q in zip(inside, exp)):
                hit = i
                break
        if hit is None:
            ok = False
            print(f"    FAIL  {name:26s} {ew:.1f} x {eh:.1f} with {exp} — not found")
        else:
            used[hit] += 1
            print(f"    OK    {name:26s} {found_outlines[hit][0]:7.2f} x {found_outlines[hit][1]:6.2f}  "
                  f"holes {found_outlines[hit][2]}")
    for L in (150.0, 50.0):
        r_ok = any(abs(w - L) < 0.06 or abs(h - L) < 0.06 for w, h in all_rulers)
        ok &= r_ok
        print(f"    {'OK  ' if r_ok else 'FAIL'}  scale ruler {L:g} mm")
    want_c = sum(sum(1 for *_, k, _ in half_holes(P, h) if k == "hole") for P in (R, Lp) for h in (1, 2)) + 2
    c_ok, k_ok = n_circ == want_c, n_keys == 2
    ok &= c_ok and k_ok
    print(f"    {'OK  ' if c_ok else 'FAIL'}  round holes: {n_circ} (want {want_c})")
    print(f"    {'OK  ' if k_ok else 'FAIL'}  axle keys Ø10.4 x 8.9: {n_keys} (want 2)")
    print("\n  " + ("ALL CHECKS PASSED — the sheet is true 1:1 and matches the model."
                    if ok else "*** VERIFICATION FAILED ***"))
    return ok


if __name__ == "__main__":
    G = geometry()
    print("  geometry from the SCAD:", G)
    R, Lp = plate(G, "right"), plate(G, "left")
    render(G, R, Lp)
    sys.exit(0 if verify(G, R, Lp) else 1)
