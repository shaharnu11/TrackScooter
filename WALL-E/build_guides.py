#!/usr/bin/env python3
"""
Build the WALL-E guide book: one HTML page per domain, plus an index that
states the order to read and do things in.

    cd WALL-E && python3 build_guides.py

Why this exists: the project is ~20 markdown files and nobody could tell what
to read first, or which file answers "what do I do now?". The markdown stays
the source of truth — this script only groups it into domains and renders it.
Re-run it after editing any doc. Output goes to WALL-E/guide/ and is safe to
delete at any time.

No third-party modules: this machine has neither `markdown` nor `pandoc`, so
the converter below is written out in full. It covers the subset of markdown
the docs actually use — headings, lists, tables, fenced code, quotes, rules,
and inline bold/code/links.
"""

import html
import os
import re
import subprocess
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "guide")

# ---------------------------------------------------------------------------
#  THE DOMAINS — this list IS the order. Change it here, nowhere else.
#  (slug, number, title, one line on when you need it, [source files])
# ---------------------------------------------------------------------------
DOMAINS = [
    ("plan", "1", "The plan and the shape of the robot",
     "Read first. What is being built, in what phases, and what has to be true "
     "before each phase can start.",
     ["README.md", "docs/00-plan.md", "docs/01-architecture.md"]),

    ("buying", "2", "What to buy",
     "Read second, before you spend money. Every part, what it costs, and what "
     "it is for. Long lead items are marked.",
     ["docs/05-bom.md"]),

    ("frame", "3", "Frame, pods and steel",
     "The mechanical build: the two track pods, the face they bolt to, the "
     "rails, the battery box. Do this before any wiring.",
     ["FRAME_AND_PODS.md", "BUILD.md"]),

    ("power", "4", "Power and wiring",
     "Batteries, contactors, fusing, and the 12 V side. Do it after the frame "
     "is standing and before the brain goes in.",
     ["docs/04-power-and-wiring.md", "docs/06-why-the-batteries-are-low.md"]),

    ("electronics", "5", "Boards and firmware",
     "The three boards — Spine, Face, Brain — what each one does, and how to "
     "flash them.",
     ["firmware/README.md", "brain/README.md"]),

    ("safety", "6", "Safety and testing",
     "The rules that do not bend, the test order, and the log of what has "
     "actually been tested. Read before the first powered move.",
     ["docs/03-safety-log.md"]),

    ("glossary", "7", "Glossary",
     "Every term and abbreviation used anywhere in this project, in plain "
     "words. Look here first when a word is unfamiliar.",
     ["docs/99-glossary.md"]),
]

CSS = """
:root{--bg:#f6f5f1;--fg:#23201b;--mut:#6a6357;--line:#ddd8cc;--card:#fffdf8;
      --acc:#b8791f;--accbg:#fdf3e2;--code:#f0ece2;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
     font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:860px;margin:0 auto;padding:28px 20px 90px}
a{color:var(--acc)}
header.top{border-bottom:2px solid var(--line);margin-bottom:26px;padding-bottom:14px}
header.top .kicker{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
h1{font-size:30px;line-height:1.25;margin:.25em 0 .2em}
h2{font-size:23px;margin:1.9em 0 .5em;padding-top:.3em;border-top:1px solid var(--line)}
h3{font-size:19px;margin:1.5em 0 .4em}
h4,h5,h6{font-size:16px;margin:1.3em 0 .3em}
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
.tw{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14.5px;background:var(--card)}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--code)}
hr{border:0;border-top:1px solid var(--line);margin:1.8em 0}
.nav{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px}
.nav a{display:inline-block;padding:5px 11px;border:1px solid var(--line);
       border-radius:999px;background:var(--card);text-decoration:none;font-size:13.5px}
.nav a.here{background:var(--acc);border-color:var(--acc);color:#fff}
.card{display:block;background:var(--card);border:1px solid var(--line);
      border-radius:10px;padding:14px 16px;margin:10px 0;text-decoration:none;color:inherit}
.card:hover{border-color:var(--acc)}
.card .n{display:inline-block;min-width:26px;height:26px;line-height:26px;
         text-align:center;border-radius:50%;background:var(--acc);color:#fff;
         font-size:14px;margin-right:9px}
.card .t{font-weight:600;font-size:17px}
.card .w{color:var(--mut);font-size:14.5px;margin:.4em 0 0 35px}
.src{color:var(--mut);font-size:13px;margin:.35em 0 0 35px}
.lead{font-size:17px;color:var(--mut)}
.note{background:var(--accbg);border:1px solid var(--line);border-left:3px solid var(--acc);
      border-radius:0 8px 8px 0;padding:12px 14px;margin:18px 0;font-size:15px}
.toc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px}
.toc div{font-size:13px;text-transform:uppercase;letter-spacing:.07em;color:var(--mut);margin-bottom:6px}
.toc ul{margin:0;padding-left:18px} .toc li{margin:.15em 0;font-size:14.5px}
.filehdr{margin-top:2.4em;font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;
         color:var(--mut);border-bottom:1px solid var(--line);padding-bottom:4px}
footer{margin-top:50px;padding-top:14px;border-top:1px solid var(--line);
       color:var(--mut);font-size:13.5px}
@media (prefers-color-scheme:dark){
  :root{--bg:#16150f;--fg:#ece7dc;--mut:#9c9384;--line:#35322a;--card:#1e1c16;
        --acc:#d99c3c;--accbg:#2a2318;--code:#26241d;}
}
"""

# ---------------------------------------------------------------------------
#  markdown -> html, the subset the docs use
# ---------------------------------------------------------------------------

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    return re.sub(r"[\s_]+", "-", s)[:60] or "section"


def convert(md, heading_shift=1, anchors=None):
    """Return HTML. heading_shift pushes '# x' down so the page keeps one h1."""
    out, lines, i = [], md.split("\n"), 0
    listst = []          # open list tags, outermost first

    def close_lists(to=0):
        while len(listst) > to:
            out.append("</%s>" % listst.pop())

    while i < len(lines):
        ln = lines[i].rstrip()
        s = ln.strip()

        if s.startswith("```"):
            close_lists()
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue

        if not s:
            close_lists()
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            close_lists()
            lvl = min(len(m.group(1)) + heading_shift, 6)
            txt = m.group(2).strip().rstrip("#").strip()
            a = slugify(txt)
            if anchors is not None and lvl <= 3:
                anchors.append((lvl, txt, a))
            out.append('<h%d id="%s">%s</h%d>' % (lvl, a, inline(txt), lvl))
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        if s.startswith("|"):
            close_lists()
            rows = []
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
            close_lists()
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + convert("\n".join(buf), heading_shift) + "</blockquote>")
            continue

        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", ln)
        if m:
            depth = len(m.group(1)) // 2 + 1
            tag = "ul" if m.group(2) in "-*+" else "ol"
            while len(listst) > depth:
                out.append("</%s>" % listst.pop())
            if len(listst) < depth:
                while len(listst) < depth:
                    out.append("<%s>" % tag)
                    listst.append(tag)
            item = [m.group(3)]
            i += 1
            while i < len(lines):                      # wrapped continuation
                nxt = lines[i]
                if (nxt.strip() and not re.match(r"^\s*([-*+]|\d+[.)])\s", nxt)
                        and not nxt.strip().startswith(("|", "#", "```", ">"))
                        and len(nxt) - len(nxt.lstrip()) >= len(m.group(1)) + 2):
                    item.append(nxt.strip())
                    i += 1
                else:
                    break
            out.append("<li>" + inline(" ".join(item)) + "</li>")
            continue

        close_lists()
        para = [s]
        i += 1
        while i < len(lines):
            n = lines[i].strip()
            if (not n or n.startswith(("|", "#", "```", ">", "---"))
                    or re.match(r"^([-*+]|\d+[.)])\s", n)):
                break
            para.append(n)
            i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")

    close_lists()
    return "\n".join(out)


# ---------------------------------------------------------------------------
#  page shell
# ---------------------------------------------------------------------------

def nav(here):
    bits = ['<a href="index.html"%s>Start here</a>'
            % ("" if here else ' class="here"')]
    for slug, num, title, _when, _src in DOMAINS:
        short = title.split(",")[0].split(" and ")[0]
        bits.append('<a href="%s.html"%s>%s. %s</a>'
                    % (slug, ' class="here"' if here == slug else "", num, short))
    return '<nav class="nav">' + "".join(bits) + "</nav>"


def page(title, kicker, body, here, extra_head=""):
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>%s</title><style>%s</style>%s</head><body><div class=\"wrap\">"
            "%s<header class=\"top\"><div class=\"kicker\">%s</div><h1>%s</h1></header>"
            "%s<footer>Generated from the markdown in this repo by "
            "<code>build_guides.py</code> on %s. Do not edit these HTML files — edit "
            "the markdown and run the script again.</footer></div></body></html>"
            % (html.escape(title), CSS, extra_head, nav(here), html.escape(kicker),
               html.escape(title), body, date.today().isoformat()))


def read(rel):
    p = os.path.join(HERE, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return f.read()


def build_domain(slug, num, title, when, sources):
    anchors, parts, used, missing = [], [], [], []
    for rel in sources:
        md = read(rel)
        if md is None:
            missing.append(rel)
            continue
        used.append(rel)
        parts.append('<p class="filehdr">from %s</p>' % html.escape(rel))
        parts.append(convert(md, heading_shift=1, anchors=anchors))
    toc = ""
    if len(anchors) > 2:
        toc = ('<div class="toc"><div>On this page</div><ul>'
               + "".join('<li><a href="#%s">%s</a></li>' % (a, html.escape(t))
                         for lvl, t, a in anchors if lvl <= 2)
               + "</ul></div>")
    head = ('<p class="lead">%s</p>' % html.escape(when)) + toc
    if missing:
        head += ('<div class="note">Missing source file(s): %s</div>'
                 % html.escape(", ".join(missing)))
    body = head + "\n".join(parts)
    with open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8") as f:
        f.write(page(title, "WALL-E guide · part " + num, body, slug))
    return used


def build_index():
    cards = []
    for slug, num, title, when, sources in DOMAINS:
        cards.append(
            '<a class="card" href="%s.html"><span class="n">%s</span>'
            '<span class="t">%s</span><div class="w">%s</div>'
            '<div class="src">%s</div></a>'
            % (slug, num, html.escape(title), html.escape(when),
               html.escape(" · ".join(sources))))
    body = (
        '<p class="lead">Seven parts, in the order you need them. Each part is '
        'one page. If you only have five minutes, read part 1.</p>'
        '<div class="note"><strong>The rule that comes before everything:</strong> '
        'the two track pods are already built. Nothing in this project changes '
        'them, and no new hole goes into one. Their numbers live in '
        '<code>pod_interface.scad</code>, checked against the newest pod '
        'revision on disk by <code>./pod_latest.sh</code> + '
        '<code>check_pod_interface.scad</code>. If that check ever says '
        'MISMATCH, stop — every dimension downstream is wrong.</div>'
        + "".join(cards) +
        '<h2 id="doing">How to actually work in this repo</h2>'
        '<ol>'
        '<li>Change the model in <code>cad/walle_frame.scad</code>, or the pod '
        'numbers in <code>pod_interface.scad</code>.</li>'
        '<li>Run <code>./render_all.sh</code>. It points at the newest pod '
        'revision, checks the interface, runs every guard, then redraws the '
        'sheets and views. It stops at the first thing that does not agree.</li>'
        '<li>Run <code>python3 build_guides.py</code> if you edited any '
        'markdown, so these pages match.</li>'
        '<li>Commit. The PNGs in <code>blueprint/</code> and <code>cad/</code> '
        'are outputs — never hand-edit them.</li>'
        '</ol>')
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page("WALL-E build guide", "Track-pod robot · guide book", body, None))


def main():
    os.makedirs(OUT, exist_ok=True)
    seen = []
    for d in DOMAINS:
        seen += build_domain(*d)
    build_index()

    # Which markdown files did NOT make it into any domain? A doc nobody can
    # reach from the index is a doc nobody reads.
    try:
        tracked = subprocess.run(["git", "ls-files", "*.md"], cwd=HERE,
                                 capture_output=True, text=True, check=True
                                 ).stdout.split()
    except Exception:
        tracked = []
    orphans = [f for f in tracked if f not in seen]
    print("guide/ written: index.html + %d domain pages" % len(DOMAINS))
    if orphans:
        print("NOT in any domain page: " + ", ".join(orphans))


if __name__ == "__main__":
    main()
