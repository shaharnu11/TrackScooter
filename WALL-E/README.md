# WALL-E

A two-track robot built on the two track pods in `../archive/`, for Midburn in the Negev
desert. The pods are already built; nothing here changes them.

## The guide is one file

**[`WALLE-GUIDE.html`](WALLE-GUIDE.html)** — open it in a browser. It is the whole project,
in order: what it is, the plan, how it works, what to buy, the frame and pod joint, the build
steps with the drawings, power and wiring, firmware, safety, glossary.

Every drawing is inside that file. There are no image files to lose. For a paper copy or a
PDF, open it and print — each part starts on a new page, and the blueprint sheets are vector,
so they stay sharp.

## Every document also has its own page

Each markdown file has an HTML twin beside it, same name: `docs/00-plan.md` →
[`docs/00-plan.html`](docs/00-plan.html), [`docs/BUILD.html`](docs/BUILD.html),
[`docs/FRAME_AND_PODS.html`](docs/FRAME_AND_PODS.html), and so on. Use one when you want a
single topic — to hand to the welder, to read on a phone, or to print on its own. Each page
is self-contained (drawings included) and carries links to all the others.

Both the guide and the pages come from the same markdown, built by the same script, so they
cannot disagree.

## The folder

```
WALL-E/
  WALLE-GUIDE.html   the whole project in one file. Generated — do not edit it
  build_guide.py     builds the guide AND one page per document
  docs/              all the words: X.md is the source, X.html is generated
  cad/               the model, the pod interface, and the render script
  firmware/          Spine (Teensy) and Face (ESP32) code
  brain/             Brain (Jetson) code
  build/             scratch drawings. Not committed. Safe to delete
```

## To change something

Edit the markdown in `docs/`, or the model in `cad/`, then:

```sh
cd WALL-E
cad/render_all.sh       # checks the pods, runs every guard, redraws everything
python3 build_guide.py  # rebuilds WALLE-GUIDE.html and every document page
```

`cad/render_all.sh` refuses to draw anything if the pod interface check or the guards fail, so
a clean run is also proof that the change is consistent. It ends by rebuilding the guide, so
usually one command is enough.

## The one rule

The pods are **built**. No new hole goes into a built pod. Their 23 numbers live only in
`cad/pod_interface.scad`, and `cad/check_pod_interface.scad` compares that file against the
**newest** pod revision in `../archive/` — `cad/pod_latest.sh` finds it, so nothing is ever
pinned to an old revision by hand. If the check says MISMATCH, stop and fix it first.

As of 2026-09-22 all 23 agree with `rev013-double-shear`.
