#!/usr/bin/env python3
"""
Build WALLE-GUIDE.html — ONE file that contains the whole build guide.

    cd WALL-E && python3 build_guide.py

WHY ONE FILE
    You take this to a workshop, or you send it to somebody. One file, no
    folder of images to lose, no links that break. Every drawing is INSIDE the
    HTML: the blueprint sheets as vector SVG (so they print sharp at any size),
    the 3D views as embedded images. There are no .png files in this project.

    To get a PDF: open it in a browser and print to PDF. The stylesheet starts
    each part on a new page and hides the navigation.

WHERE THE CONTENT COMES FROM
    The markdown in docs/, firmware/ and brain/ is the source of truth. This
    script only orders it, converts it, and drops the drawings in. Edit the
    markdown, run this again.

WHERE THE DRAWINGS COME FROM
    cad/render_all.sh renders them into build/, which is scratch and is not
    committed. In the markdown, refer to one as a normal image:

        ![Sheet 2 — frame weldment](fig/s2.svg)

    The name after fig/ is the file in build/. Nothing else is special.

No third-party modules: no `markdown` and no `pandoc` on this machine, so the
converter is written out in full below.
"""

import base64
import html
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "build")
OUTFILE = os.path.join(HERE, "WALLE-GUIDE.html")

# ---------------------------------------------------------------------------
#  THE ORDER. This list is the guide. Nothing else decides what goes where.
#  (part number, title, "read this when", [source markdown files])
# ---------------------------------------------------------------------------
PARTS = [
    ("1", "What this robot is",
     "Read first. Ten minutes. What is being built and why it is shaped this way.",
     ["docs/02-overview.md"]),

    ("2", "The plan, the phases and the money",
     "Read second. The order of the whole project, what each phase must prove "
     "before the next one starts, the budget and the risks.",
     ["docs/00-plan.md"]),

    ("3", "How it works: three computers and the safety rules",
     "Read before you buy electronics. The three boards, what each one decides, "
     "and the rules that stop the robot.",
     ["docs/01-architecture.md"]),

    ("4", "What to buy",
     "Read before you spend money. Every part, the price, the lead time. Long "
     "lead items are marked — order those first.",
     ["docs/05-bom.md"]),

    ("5", "Frame and pods: where the steel meets the built pods",
     "Read before you cut, drill or weld anything. The one joint that the whole "
     "robot hangs on.",
     ["docs/FRAME_AND_PODS.md"]),

    ("6", "Build it, step by step",
     "The steps in order, with a check at the end of each one. The drawings are "
     "in this part.",
     ["docs/BUILD.md"]),

    ("7", "Power and wiring",
     "Do this after the frame stands and before the brain goes in. Batteries, "
     "contactors, fuses, and the emergency stop chain.",
     ["docs/04-power-and-wiring.md", "docs/06-why-the-batteries-are-low.md"]),

    ("8", "Boards and firmware",
     "Flashing the Spine and the Face, and running the Brain.",
     ["firmware/README.md", "brain/README.md"]),

    ("9", "Safety and testing",
     "Read before the first powered move, and keep the log up to date by hand.",
     ["docs/03-safety-log.md"]),

    ("10", "Glossary",
     "Every technical word used in this guide, in plain language. Look here "
     "first when a word is unfamiliar.",
     ["docs/99-glossary.md"]),
]

CSS = """
:root{--bg:#f7f6f2;--fg:#201d18;--mut:#6b6458;--line:#dcd7cb;--card:#fffdf8;
      --acc:#b0761d;--accbg:#fbf2e0;--code:#efebe1;--warn:#8d2f20;}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);
     font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:0 22px 80px}
a{color:var(--acc)}
h1{font-size:34px;line-height:1.2;margin:.2em 0}
h2{font-size:25px;margin:1.8em 0 .5em;padding-top:.35em;border-top:1px solid var(--line)}
h3{font-size:20px;margin:1.5em 0 .4em}
h4,h5,h6{font-size:16.5px;margin:1.3em 0 .3em}
p,ul,ol,table,pre,blockquote{margin:.7em 0}
li{margin:.25em 0}
code{background:var(--code);padding:1px 5px;border-radius:4px;
     font:13.5px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:var(--card);border:1px solid var(--line);border-radius:8px;
    padding:12px 14px;overflow-x:auto}
pre code{background:none;padding:0}
blockquote{border-left:3px solid var(--acc);background:var(--accbg);
           padding:.5em 14px;border-radius:0 6px 6px 0}
blockquote p:first-child{margin-top:0} blockquote p:last-child{margin-bottom:0}
.tw{overflow-x:auto;margin:.8em 0}
table{border-collapse:collapse;width:100%;font-size:14.5px;background:var(--card)}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--code)}
hr{border:0;border-top:1px solid var(--line);margin:1.8em 0}

/* ---- cover ---- */
.cover{padding:60px 0 26px;border-bottom:3px solid var(--fg)}
.cover .sub{font-size:19px;color:var(--mut);margin-top:.3em}
.cover .meta{font-size:13.5px;color:var(--mut);margin-top:1.4em}

/* ---- contents ---- */
.toc{background:var(--card);border:1px solid var(--line);border-radius:12px;
     padding:8px 18px 14px;margin:26px 0}
.toc h2{border:0;margin:.8em 0 .3em;font-size:19px}
.toc ol{list-style:none;padding:0;margin:0}
.toc>ol>li{border-top:1px solid var(--line);padding:9px 0}
.toc>ol>li:first-child{border-top:0}
.toc .n{display:inline-block;min-width:28px;height:28px;line-height:28px;
        text-align:center;border-radius:50%;background:var(--acc);color:#fff;
        font-size:14px;margin-right:10px;font-weight:600}
.toc .t{font-weight:600;font-size:17px;text-decoration:none;color:inherit}
.toc .t:hover{color:var(--acc)}
.toc .w{color:var(--mut);font-size:14px;margin:.35em 0 0 38px}
.toc .subs{margin:.4em 0 0 38px;font-size:13.5px;color:var(--mut);
            display:flex;flex-wrap:wrap;gap:3px 14px}
.toc .subs a{color:var(--mut);text-decoration:none}
.toc .subs a:hover{color:var(--acc)}

/* ---- parts ---- */
.part{padding-top:26px}
.part-hd{border-top:3px solid var(--fg);padding-top:16px;margin-top:40px}
.part-hd .kick{font-size:12.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--acc);font-weight:700}
.part-hd h1{font-size:29px;margin:.15em 0 .25em}
.part-hd .lead{color:var(--mut);font-size:16.5px;margin:0}
.src{color:var(--mut);font-size:12.5px;letter-spacing:.05em;text-transform:uppercase;
     border-bottom:1px solid var(--line);padding-bottom:4px;margin:2.4em 0 .8em}

/* ---- figures ---- */
figure{margin:1.4em 0;background:var(--card);border:1px solid var(--line);
       border-radius:10px;padding:14px}
figure img{display:block;max-width:100%;height:auto;margin:0 auto}
figure svg{display:block;width:100%;height:auto}
figure svg path{fill:#16130e;stroke:none}
figcaption{color:var(--mut);font-size:13.5px;margin-top:10px;text-align:center}
.sheet figure{background:#fff}

.pagehd{padding:34px 0 20px}
.pagehd .kick{font-size:12.5px;letter-spacing:.11em;text-transform:uppercase;
              color:var(--acc);font-weight:700}
.pagenav{display:flex;flex-wrap:wrap;gap:7px;margin:20px 0 6px}
.pagenav a{display:inline-block;padding:4px 11px;border:1px solid var(--line);
           border-radius:999px;background:var(--card);text-decoration:none;
           color:var(--mut);font-size:13px}
.pagenav a.here{background:var(--acc);border-color:var(--acc);color:#fff}
.pagetoc ol{margin:0;padding-left:20px;list-style:decimal}
.pagetoc li{font-size:14.5px;margin:.15em 0}
.pagetoc h2{border:0;margin:.6em 0 .4em;font-size:17px}

.note{background:var(--accbg);border:1px solid var(--line);border-left:4px solid var(--acc);
      border-radius:0 8px 8px 0;padding:13px 16px;margin:20px 0;font-size:15px}
.note strong:first-child{color:var(--warn)}
.top{position:fixed;right:16px;bottom:16px;background:var(--acc);color:#fff;
     text-decoration:none;border-radius:999px;padding:9px 15px;font-size:13.5px;
     box-shadow:0 2px 8px rgba(0,0,0,.2)}
footer{margin-top:44px;padding-top:14px;border-top:1px solid var(--line);
       color:var(--mut);font-size:13.5px}

@media print{
  body{background:#fff;font-size:11.5pt}
  .wrap{max-width:none;padding:0}
  .top{display:none}
  .part-hd{break-before:page;page-break-before:always}
  figure,table,pre,blockquote{break-inside:avoid;page-break-inside:avoid}
  h2,h3{break-after:avoid;page-break-after:avoid}
  a{color:inherit;text-decoration:none}
  .toc{break-after:page;page-break-after:always}
}
@media (prefers-color-scheme:dark){
  :root{--bg:#15140f;--fg:#ece7dc;--mut:#9b9284;--line:#34302a;--card:#1d1b15;
        --acc:#d99c3c;--accbg:#29221a;--code:#25231c;--warn:#e0705c;}
  figure svg path{fill:#e8e3d8}
  .sheet figure{background:#14120e}
}
"""

# ---------------------------------------------------------------------------
#  figures: pull the file out of build/ and put it INSIDE the html
# ---------------------------------------------------------------------------
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".webp": "image/webp"}
missing_figs = []


def figure(name, caption):
    path = os.path.join(FIGS, name)
    cap = ('<figcaption>%s</figcaption>' % inline(caption)) if caption else ""
    if not os.path.exists(path):
        missing_figs.append(name)
        return ('<figure><div class="note"><strong>Drawing missing:</strong> '
                'build/%s. Run <code>cad/render_all.sh</code>, then build this '
                'guide again.</div>%s</figure>' % (html.escape(name), cap))
    ext = os.path.splitext(name)[1].lower()
    cls = ' class="sheet"' if ext == ".svg" else ""
    if ext == ".svg":
        with open(path, encoding="utf-8") as f:
            svg = f.read()
        svg = re.sub(r"<\?xml.*?\?>", "", svg, flags=re.S)
        svg = re.sub(r"<!DOCTYPE.*?>", "", svg, flags=re.S)
        svg = re.sub(r"<title>.*?</title>", "", svg, flags=re.S)
        # drop the fixed mm size so it scales to the page, keep the viewBox
        svg = re.sub(r'(<svg[^>]*?)\s+width="[^"]*"', r"\1", svg, count=1)
        svg = re.sub(r'(<svg[^>]*?)\s+height="[^"]*"', r"\1", svg, count=1)
        # colours come from the stylesheet, so the drawing follows the theme
        svg = re.sub(r'\s+(fill|stroke)="[^"]*"', "", svg)
        body = svg.strip()
    else:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        body = '<img alt="%s" src="data:%s;base64,%s">' % (
            html.escape(caption or name), MIME.get(ext, "image/png"), b64)
    return "<figure%s>%s%s</figure>" % (cls, body, cap)


# ---------------------------------------------------------------------------
#  markdown -> html, the subset these docs use
# ---------------------------------------------------------------------------
IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)\s]+)\)\s*$")


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", t)
    return t


used_ids = set()


def slugify(s, prefix=""):
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    base = (prefix + re.sub(r"[\s_]+", "-", s))[:70] or "section"
    out, n = base, 2
    while out in used_ids:
        out, n = "%s-%d" % (base, n), n + 1
    used_ids.add(out)
    return out


def convert(md, shift=1, anchors=None, prefix=""):
    out, lines, i = [], md.split("\n"), 0
    listst = []

    def close(to=0):
        while len(listst) > to:
            out.append("</%s>" % listst.pop())

    while i < len(lines):
        ln = lines[i].rstrip()
        s = ln.strip()

        if s.startswith("```"):
            close(); i += 1; buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i])); i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue

        if not s:
            close(); i += 1; continue

        m = IMG_RE.match(s)                       # a figure on its own line
        if m:
            close()
            cap, src = m.group(1), m.group(2)
            if src.startswith("fig/"):
                out.append(figure(src[4:], cap))
            else:
                out.append('<figure><img alt="%s" src="%s">%s</figure>'
                           % (html.escape(cap), html.escape(src),
                              "<figcaption>%s</figcaption>" % inline(cap) if cap else ""))
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            close()
            lvl = min(len(m.group(1)) + shift, 6)
            txt = m.group(2).strip().rstrip("#").strip()
            a = slugify(txt, prefix)
            if anchors is not None and lvl == 2:
                anchors.append((txt, a))
            out.append('<h%d id="%s">%s</h%d>' % (lvl, a, inline(txt), lvl))
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            close(); out.append("<hr>"); i += 1; continue

        if s.startswith("|"):
            close(); rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head = rows[0] if len(rows) > 1 and all(
                re.match(r"^:?-{2,}:?$", c) for c in rows[1]) else None
            body = rows[2:] if head else rows
            t = ['<div class="tw"><table>']
            if head:
                t.append("<thead><tr>" + "".join("<th>%s</th>" % inline(c) for c in head)
                         + "</tr></thead>")
            t.append("<tbody>")
            for r in body:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue

        if s.startswith(">"):
            close(); buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip()); i += 1
            out.append("<blockquote>" + convert("\n".join(buf), shift, None, prefix)
                       + "</blockquote>")
            continue

        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", ln)
        if m:
            depth = len(m.group(1)) // 2 + 1
            tag = "ul" if m.group(2) in "-*+" else "ol"
            while len(listst) > depth:
                out.append("</%s>" % listst.pop())
            while len(listst) < depth:
                out.append("<%s>" % tag); listst.append(tag)
            item = [m.group(3)]; i += 1
            while i < len(lines):
                nxt = lines[i]
                if (nxt.strip() and not re.match(r"^\s*([-*+]|\d+[.)])\s", nxt)
                        and not nxt.strip().startswith(("|", "#", "```", ">", "!["))
                        and len(nxt) - len(nxt.lstrip()) >= len(m.group(1)) + 2):
                    item.append(nxt.strip()); i += 1
                else:
                    break
            out.append("<li>" + inline(" ".join(item)) + "</li>")
            continue

        close(); para = [s]; i += 1
        while i < len(lines):
            n = lines[i].strip()
            if (not n or n.startswith(("|", "#", "```", ">", "---", "!["))
                    or re.match(r"^([-*+]|\d+[.)])\s", n)):
                break
            para.append(n); i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")

    close()
    return "\n".join(out)


# ---------------------------------------------------------------------------
#  the opening part, written here because it is about the guide itself
# ---------------------------------------------------------------------------
HOW_TO_USE = """
## Before anything else

**The two track pods are already built.** Nothing in this project changes them, and
**no new hole goes into a built pod.** Every number about them lives in one file,
`cad/pod_interface.scad`, and a checker compares that file against the newest pod
revision in `../archive/`. If the checker ever says MISMATCH, stop: every dimension
after it is wrong.

## The order of work

1. **Read parts 1 to 3.** Do not buy anything yet. The parts list only makes sense
   after the plan.
2. **Order the long-lead parts** from part 4 — the contactors and the bench supply
   take weeks. Everything else can wait.
3. **Measure the real pods** against the table in part 5. Five minutes with a tape
   measure, and it is the one thing that, if wrong, makes the frame scrap.
4. **Cut and weld the frame** with part 6 and the sheets in it. Sheet 2 is the one
   the welder gets.
5. **Wire the power** with part 7. Nothing moves yet — this ends with a bench test.
6. **Flash the boards** with part 8, on the bench, motors not connected.
7. **Work through part 9** before the robot moves near a person, and fill the log in
   by hand as you go.

Parts 1 to 5 are reading and buying. Parts 6 to 9 are doing. If you only have five
minutes, read part 1.

## How to get a PDF of this guide

Open this file in a browser and print (Cmd-P / Ctrl-P), then "Save as PDF". Each part
starts on a new page and the drawings are vector, so they stay sharp at any zoom.

## How to change it

The words come from the markdown files in `docs/`, `firmware/` and `brain/`. The
drawings come from the OpenSCAD model in `cad/`. Nothing in this HTML is written by
hand, so do not edit it — edit the source and run:

```sh
cd WALL-E
cad/render_all.sh       # checks the pods, runs every guard, redraws everything
python3 build_guide.py  # rebuilds this one file
```

`cad/render_all.sh` refuses to draw anything if the pod numbers or the guards do not
pass, so a clean run is also the model's own proof that the change is consistent.

## One page per document

Every markdown file also gets its own HTML page beside it, with the same name:
`docs/00-plan.md` becomes `docs/00-plan.html`. Use those when you want one topic on
its own — to send to the welder, to read on a phone, or to print a single section.
They are built by the same script from the same words, so they cannot drift from this
guide. The whole project in one file is what you are reading now.
"""


def read(rel):
    p = os.path.join(HERE, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        md = f.read()
    # Each doc starts with its own "# 04 — Power and wiring" title, and the part
    # header above it already says that. Printing both reads like a stutter, so
    # drop the document's leading H1 (and only a LEADING one).
    lines = md.split("\n")
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        return "\n".join(lines[i + 1:]) if re.match(r"^#\s+\S", ln) else md
    return md


# ---------------------------------------------------------------------------
#  ONE PAGE PER MARKDOWN FILE
#
#  The guide above is the whole project in one file. These are the same words
#  cut up the way the folder is: docs/00-plan.md -> docs/00-plan.html, beside
#  it, same name. Send one to the welder without sending all of it.
#
#  Each page is self-contained too: the drawings are embedded, exactly as in
#  the guide, so a page still works when it is the only file you copied.
# ---------------------------------------------------------------------------
MD_LINK = re.compile(r'href="(?!https?:|#|mailto:)([^"]+)\.md(#[^"]*)?"')


def all_markdown():
    """Every .md in the project, guide order first, then whatever is left."""
    found = []
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in ("build", ".git", "__pycache__")]
        for f in files:
            if f.endswith(".md"):
                found.append(os.path.relpath(os.path.join(root, f), HERE))
    order = ["README.md"] + [src for _, _, _, srcs in PARTS for src in srcs]
    ordered = [p for p in order if p in found]
    return ordered + sorted(p for p in found if p not in ordered)


def doc_title(raw, rel):
    for ln in raw.split("\n"):
        if ln.strip():
            m = re.match(r"^#\s+(.*)$", ln.strip())
            return m.group(1).strip() if m else os.path.basename(rel)
    return os.path.basename(rel)


def build_pages():
    pages, titles = all_markdown(), {}
    for rel in pages:
        with open(os.path.join(HERE, rel), encoding="utf-8") as f:
            titles[rel] = doc_title(f.read(), rel)

    written = []
    for rel in pages:
        outp = os.path.splitext(rel)[0] + ".html"
        here_dir = os.path.dirname(os.path.join(HERE, outp)) or HERE

        def rel_to(target):
            return os.path.relpath(os.path.join(HERE, target), here_dir)

        used_ids.clear()                      # anchors are per page, not global
        anchors = []
        body = convert(read(rel), shift=1, anchors=anchors)
        # a link to another document should open that document's PAGE
        body = MD_LINK.sub(lambda m: 'href="%s.html%s"' % (m.group(1), m.group(2) or ""),
                           body)

        nav = "".join(
            '<a href="%s"%s>%s</a>'
            % (rel_to(os.path.splitext(o)[0] + ".html"),
               ' class="here"' if o == rel else "", html.escape(titles[o]))
            for o in pages)
        toc = ""
        if len(anchors) > 2:
            toc = ('<div class="toc pagetoc"><h2>On this page</h2><ol>'
                   + "".join('<li><a href="#%s">%s</a></li>' % (a, html.escape(t))
                             for t, a in anchors)
                   + "</ol></div>")

        page = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
                "<title>%s — WALL-E</title><style>%s</style></head><body>"
                "<div class=\"wrap\">"
                "<header class=\"cover pagehd\"><div class=\"kick\">WALL-E · %s</div>"
                "<h1>%s</h1>"
                "<div class=\"meta\">One document of the project. The whole thing in "
                "reading order is in <a href=\"%s\">the build guide</a>. "
                "Generated %s from <code>%s</code> — do not edit this file.</div></header>"
                "<nav class=\"pagenav\">%s</nav>%s%s"
                "<footer>Generated by <code>build_guide.py</code> from <code>%s</code>. "
                "Edit the markdown, not this page.</footer>"
                "</div><a class=\"top\" href=\"#\">Top</a></body></html>"
                % (html.escape(titles[rel]), CSS, html.escape(rel),
                   html.escape(titles[rel]), rel_to("WALLE-GUIDE.html"),
                   date.today().isoformat(), html.escape(rel), nav, toc, body,
                   html.escape(rel)))
        with open(os.path.join(HERE, outp), "w", encoding="utf-8") as f:
            f.write(page)
        written.append(outp)
    return written


def main():
    parts_html, toc, missing_docs = [], [], []

    # part 0 — how to use the guide
    anchors = []
    body0 = convert(HOW_TO_USE, shift=1, anchors=anchors, prefix="p0-")
    parts_html.append(
        '<section class="part" id="part-0"><div class="part-hd">'
        '<div class="kick">Start here</div><h1>How to use this guide</h1>'
        '<p class="lead">What to read, in what order, and what to do first.</p>'
        "</div>" + body0 + "</section>")
    toc.append(("0", "How to use this guide",
                "What to read, in what order, and what to do first.",
                "part-0", anchors))

    for num, title, when, sources in PARTS:
        anchors, chunks = [], []
        for rel in sources:
            md = read(rel)
            if md is None:
                missing_docs.append(rel)
                continue
            if len(sources) > 1:
                chunks.append('<p class="src">from %s</p>' % html.escape(rel))
            chunks.append(convert(md, shift=1, anchors=anchors, prefix="p%s-" % num))
        pid = "part-%s" % num
        parts_html.append(
            '<section class="part" id="%s"><div class="part-hd">'
            '<div class="kick">Part %s</div><h1>%s</h1><p class="lead">%s</p></div>%s</section>'
            % (pid, num, html.escape(title), html.escape(when), "\n".join(chunks)))
        toc.append((num, title, when, pid, anchors))

    # A doc that links to "BUILD.md" means part 6 of this guide, not a file on
    # disk. Point it at the part, so no link inside the guide leaves the guide.
    part_of = {}
    for num, _t, _w, sources in PARTS:
        for src in sources:
            part_of[os.path.basename(src)] = "#part-%s" % num
    joined = "\n".join(parts_html)
    joined = re.sub(r'href="(?!https?:|#|mailto:)([^"]*?)([^/"]+\.md)(#[^"]*)?"',
                    lambda m: 'href="%s"' % part_of.get(m.group(2),
                                                        m.group(0)[6:-1]),
                    joined)
    parts_html = [joined]

    toc_html = ['<nav class="toc"><h2>Contents</h2><ol>']
    for num, title, when, pid, anchors in toc:
        subs = "".join('<a href="#%s">%s</a>' % (a, html.escape(t)) for t, a in anchors[:9])
        toc_html.append(
            '<li><span class="n">%s</span><a class="t" href="#%s">%s</a>'
            '<div class="w">%s</div>%s</li>'
            % (num, pid, html.escape(title), html.escape(when),
               '<div class="subs">%s</div>' % subs if subs else ""))
    toc_html.append("</ol></nav>")

    warn = ""
    if missing_docs or missing_figs:
        bits = []
        if missing_docs:
            bits.append("missing source files: " + ", ".join(missing_docs))
        if missing_figs:
            bits.append("missing drawings: " + ", ".join(sorted(set(missing_figs))))
        warn = '<div class="note"><strong>Incomplete build.</strong> %s</div>' % html.escape(
            " · ".join(bits))

    doc = ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
           "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
           "<title>WALL-E — build guide</title><style>%s</style></head><body>"
           "<div class=\"wrap\">"
           "<header class=\"cover\"><h1>WALL-E</h1>"
           "<div class=\"sub\">Build guide — one file, start to finish</div>"
           "<div class=\"meta\">A two-track robot on the two built track pods, for Midburn "
           "in the Negev desert.<br>Generated %s from the markdown and the OpenSCAD model "
           "in this folder. Do not edit this file.</div></header>"
           "%s%s%s"
           "<footer>Every drawing here is generated from <code>cad/walle.scad</code> and "
           "<code>cad/walle_frame.scad</code>, which refuse to render unless the pod "
           "interface check and every guard pass.</footer>"
           "</div><a class=\"top\" href=\"#\">Top</a></body></html>"
           % (CSS, date.today().isoformat(), warn, "".join(toc_html), "\n".join(parts_html)))

    with open(OUTFILE, "w", encoding="utf-8") as f:
        f.write(doc)

    kb = os.path.getsize(OUTFILE) / 1024
    print("WALLE-GUIDE.html written — %d parts, %.0f KB" % (len(toc), kb))

    pages = build_pages()
    print("one page per document — %d written:" % len(pages))
    for pg in pages:
        print("   %-34s %6.0f KB" % (pg, os.path.getsize(os.path.join(HERE, pg)) / 1024))
    if missing_docs:
        print("  MISSING SOURCES: " + ", ".join(missing_docs))
    if missing_figs:
        print("  MISSING DRAWINGS: " + ", ".join(sorted(set(missing_figs)))
              + "   (run cad/render_all.sh)")
    return 1 if (missing_docs or missing_figs) else 0


if __name__ == "__main__":
    sys.exit(main())
