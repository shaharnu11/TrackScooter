# WALL-E

Two-track robot built on the two track pods in `../archive/`. Target: Midburn, Negev desert.

- Pods: already built. This project does not modify them.
- Drive: skid steer. No steering fork.
- Control: radio remote. Autonomous safety layer on top.

## Guide

`WALLE-GUIDE.html` — whole project, one file, in build order. Open in a browser.

- 11 parts: how to use, what it is, plan, architecture, buying, frame and pods, build steps, power, firmware, safety, glossary.
- All drawings embedded. No external image files.
- PDF: open and print. One part per page break. Sheets are vector.

## Per-document pages

Every `.md` has an `.html` twin of the same name:

- `docs/00-plan.md` → [`docs/00-plan.html`](docs/00-plan.html)
- Also [`docs/BUILD.html`](docs/BUILD.html), [`docs/FRAME_AND_PODS.html`](docs/FRAME_AND_PODS.html), and the rest.
- Each page is self-contained, drawings included, and links to the others.

Guide and pages come from the same markdown, built by the same script. They cannot disagree.

## Folder

```
WALL-E/
  WALLE-GUIDE.html   whole project, one file. Generated
  build_guide.py     generates the guide and every document page
  docs/              X.md is source, X.html is generated
  cad/               model, pod interface, render script
  firmware/          Spine (Teensy 4.0), Face (ESP32-S3)
  brain/             Brain (Dell XPS 15), Python
  build/             scratch drawings. Not committed. Deletable
```

## Rebuild

```sh
cd WALL-E
cad/render_all.sh       # pod check, guards, redraw, then rebuild the guide
python3 build_guide.py  # guide and document pages only
```

`cad/render_all.sh` stops on a failed pod check or a failed guard. A clean run is proof the change is consistent.

## Pod rule

- The pods are built. **No new hole goes into a built pod.**
- Their 23 numbers exist in one file: `cad/pod_interface.scad`.
- `cad/check_pod_interface.scad` compares that file against the newest pod revision in `../archive/`.
- `cad/pod_latest.sh` selects that revision. Nothing is pinned by hand.
- MISMATCH: stop. Every dimension downstream is wrong.

2026-09-22: 23/23 agree with `rev013-double-shear`.
