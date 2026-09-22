#!/usr/bin/env bash
# ============================================================================
#  Regenerate every blueprint sheet and every view, from walle.scad.
#
#    ./render_all.sh
#
#  Everything it writes is generated. Never hand-edit a PNG in blueprint/ or
#  cad/ — change the model and run this again.
#
#  It also runs the pod interface check first and STOPS if that fails, because
#  a mismatch there means every dimension on every sheet below it is wrong.
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")"

OSC=${OPENSCAD:-/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD}
[ -x "$OSC" ] || OSC=openscad

# OpenSCAD picks its output format from the file EXTENSION, so it cannot write
# to /dev/null. Echo-only runs go to a scratch .csg instead.
NUL=$(mktemp -t walle).csg
trap 'rm -f "$NUL"' EXIT

mkdir -p blueprint

echo "== 0. point at the newest pod revision on disk"
./pod_latest.sh

echo "== 1. does the pod interface still match the pod model?"
if "$OSC" -o "$NUL" check_pod_interface.scad 2>&1 | grep -q 'MISMATCH'; then
  "$OSC" -o "$NUL" check_pod_interface.scad 2>&1 | grep -E 'MISMATCH|DIFFERS'
  echo "!! STOPPING. pod_interface.scad disagrees with the pod model."
  echo "!! Fix that first — every dimension below it is wrong."
  exit 1
fi
"$OSC" -o "$NUL" check_pod_interface.scad 2>&1 | grep -E 'ALL [0-9]+ NUMBERS AGREE' || true

echo "== 2. do all the model guards pass?"
if "$OSC" -o "$NUL" cad/walle_frame.scad 2>&1 | grep -q 'WARN'; then
  echo "   guards reporting a warning:"
  "$OSC" -o "$NUL" cad/walle_frame.scad 2>&1 | grep 'WARN' | sed 's/^/   /'
else
  echo "   all $("$OSC" -o "$NUL" cad/walle_frame.scad 2>&1 | grep -c '"PASS') guards pass"
fi

# --- blueprint sheets. Flat 2D, so view them straight down, framed to fit.
# --render is NOT optional here. In OpenCSG preview mode every 2D difference()
# comes out FILLED, so outlines and the title block render as solid blocks and
# the sheet is unreadable. --render forces the CGAL path, which is correct.
#
# --viewall is NOT used either. It pads so generously that the drawing ends up
# filling about half the page. Each sheet draws a border of a known size, so
# the camera is aimed at that border's centre with an explicit ortho distance.
# OpenSCAD's ortho distance shows roughly dist * 0.34 of model height, hence
# the numbers below: dist = (border height + margin) / 0.34.
sheet(){ # name cx cy dist width height
  echo "   blueprint/$1.png"
  "$OSC" -o "blueprint/$1.png" --imgsize="$5,$6" --render \
    --camera="$2,$3,0,0,0,0,$4" --projection=o \
    -D "view=\"$1\"" walle.scad 2>/dev/null
}

echo "== 3. blueprint sheets"
#     name  centre x  centre y  dist  px wide  px tall
sheet s1     180        75      5900   2400 1400
sheet s2     340       295      6400   1850 1560
sheet s3     490       700      7600   1250 1800
sheet s4     315       -20      3300   1600 1200
sheet s5     250       240      4000   1150 1400

# --- solid views. Y-up model, so png_up rotates it for the camera.
solid(){ # name camera imgsize
  echo "   cad/$1.png"
  "$OSC" -o "cad/$1.png" --imgsize="$3" --camera="$2" --projection=p \
    -D png_up=true -D show_ground=false -D "render_mode=\"$4\"" \
    cad/walle_frame.scad 2>/dev/null
}
echo "== 4. solid views"
solid walle_robot_3q    1900,-1700,1100,0,0,420   1000,950  robot
solid walle_robot_front 2700,0,460,0,0,460        900,1000  robot
solid walle_robot_side  0,-2600,500,0,0,440       1000,900  robot
solid walle_frame_3q    1500,-1500,1000,0,0,300   1000,900  assembly
solid walle_frame_section 2000,-1900,1250,0,0,430 1000,900  section
solid walle_head        700,-620,950,0,0,830      900,700   head
solid walle_chest       -1250,-1100,1500,60,0,560 950,800   chest

echo "   cad/walle_shelf.png"
"$OSC" -o cad/walle_shelf.png --imgsize=1100,900 \
  --camera=0,0,0,0,0,0,0 --autocenter --viewall --projection=o \
  -D png_up=true -D shelf_labels=true -D show_ground=false \
  -D 'render_mode="shelf"' cad/walle_frame.scad 2>/dev/null

echo "   cad/walle_frame_plates.png"
"$OSC" -o cad/walle_frame_plates.png --imgsize=640,1180 \
  --camera=0,0,0,0,0,0,0 --autocenter --viewall --projection=o \
  -D 'render_mode="plates"' cad/walle_frame.scad 2>/dev/null

echo "== done. Sheets in blueprint/, views in cad/."

echo ""
echo "== guide book: one HTML page per domain, plus the index"
python3 build_guides.py
