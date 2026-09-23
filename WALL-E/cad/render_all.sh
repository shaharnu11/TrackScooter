#!/usr/bin/env bash
# ============================================================================
#  Check the model, then redraw every drawing the guide uses.
#
#    cad/render_all.sh
#
#  It writes into build/, which is scratch and is NOT committed. The drawings
#  live inside WALLE-GUIDE.html — build_guide.py puts them there. There are no
#  .png files in this project.
#
#  It STOPS if the pod interface check fails, because a mismatch there means
#  every dimension on every drawing below it is wrong.
# ============================================================================
set -euo pipefail
cd "$(dirname "$0")"
OUT=../build

OSC=${OPENSCAD:-/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD}
[ -x "$OSC" ] || OSC=openscad

# OpenSCAD picks its output format from the file EXTENSION, so it cannot write
# to /dev/null. Echo-only runs go to a scratch .csg instead.
NUL=$(mktemp -t walle).csg
trap 'rm -f "$NUL"' EXIT
mkdir -p "$OUT"

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
if "$OSC" -o "$NUL" walle_frame.scad 2>&1 | grep -q 'WARN'; then
  echo "   guards reporting a warning:"
  "$OSC" -o "$NUL" walle_frame.scad 2>&1 | grep 'WARN' | sed 's/^/   /'
else
  echo "   all $("$OSC" -o "$NUL" walle_frame.scad 2>&1 | grep -c '"PASS') guards pass"
fi

# --- blueprint sheets, as SVG. They are flat 2D, so they export as real vector
# --- drawings: sharp at any zoom, and they print properly from the guide.
# --render is NOT optional. In preview mode every 2D difference() comes out
# FILLED, so outlines and the title block render as solid blocks.
echo "== 3. blueprint sheets (vector)"
for s in s1 s2 s3 s4 s5; do
  echo "   build/$s.svg"
  "$OSC" -o "$OUT/$s.svg" --render -D "view=\"$s\"" walle.scad 2>/dev/null
done

# --- solid views. Y-up model, so png_up rotates it for the camera. These are
# --- 3D, so they cannot be vector; they get embedded in the guide as images.
solid(){ # name camera imgsize mode
  echo "   build/$1.png"
  "$OSC" -o "$OUT/$1.png" --imgsize="$3" --camera="$2" --projection=p \
    -D png_up=true -D show_ground=false -D "render_mode=\"$4\"" \
    walle_frame.scad 2>/dev/null
}
echo "== 4. solid views"
solid walle_robot_3q    1900,-1700,1100,0,0,420   1000,950  robot
solid walle_robot_front 2700,0,460,0,0,460        900,1000  robot
solid walle_robot_side  0,-2600,500,0,0,440       1000,900  robot
solid walle_frame_3q    1500,-1500,1000,0,0,300   1000,900  assembly
solid walle_frame_section 2000,-1900,1250,0,0,430 1000,900  section
solid walle_head        700,-620,950,0,0,830      900,700   head
solid walle_chest       -1250,-1100,1500,60,0,560 950,800   chest

echo "   build/walle_shelf.png"
"$OSC" -o "$OUT/walle_shelf.png" --imgsize=1100,900 \
  --camera=1400,-1600,900,0,0,450 --projection=p \
  -D png_up=true -D shelf_labels=true -D show_ground=false \
  -D 'render_mode="shelf"' walle_frame.scad 2>/dev/null

echo "   build/walle_frame_plates.png"
"$OSC" -o "$OUT/walle_frame_plates.png" --imgsize=640,1180 \
  --camera=0,0,0,0,0,0,0 --autocenter --viewall --projection=o \
  -D 'render_mode="plates"' walle_frame.scad 2>/dev/null

echo "== 5. the guide"
cd ..
python3 build_guide.py
