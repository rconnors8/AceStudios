#!/usr/bin/env python3
"""Render the work section from content/projects.json.

The site stays plain static HTML - this script just saves you from hand-editing
markup every time you add a project.

    python3 tools/build.py                 # re-render everything
    python3 tools/build.py add             # add a project, answering prompts
    python3 tools/build.py list            # show what is currently published
    python3 tools/build.py drop <slug>     # remove a project
    python3 tools/build.py drop-demo       # remove all remaining demo projects

It writes:
  - work/<slug>.html           one page per project
  - work.html                  the filterable grid (between the BUILD markers)
  - index.html                 the featured cards (between the BUILD markers)

Everything else - studio, services, journal, contact - is hand-edited and is
never touched by this script.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "content", "projects.json")

GRID_START = "<!-- BUILD:work-grid:start -->"
GRID_END = "<!-- BUILD:work-grid:end -->"
FEAT_START = "<!-- BUILD:featured:start -->"
FEAT_END = "<!-- BUILD:featured:end -->"
RECENT_START = "<!-- BUILD:recent:start -->"
RECENT_END = "<!-- BUILD:recent:end -->"
RECENT_COUNT = 6

# Filter buttons on work.html. Keep in sync with the tags you actually use.
TAGS = ["identity", "apparel", "advertising", "motion", "web", "typography", "print"]


# --------------------------------------------------------------- page shell

HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta name="theme-color" content="#0b0b0c">
<link rel="icon" href="{b}assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{b}assets/css/main.css">
<script>document.documentElement.className += " js";</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap site-header__bar">
    <a class="wordmark" href="{b}index.html"><span class="wordmark__dot" aria-hidden="true"></span> Ace Studios</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav class="nav" id="nav" data-open="false" aria-label="Primary">
      <a href="{b}work.html" aria-current="page">Work</a>
      <a href="{b}studio.html">Studio</a>
      <a href="{b}services.html">Services</a>
      <a href="{b}journal.html">Journal</a>
      <a href="{b}contact.html">Contact</a>
    </nav>
  </div>
</header>

<main id="main">
'''

FOOT = '''</main>

<footer class="site-footer">
  <div class="wrap">
    <a class="footer-cta reveal" href="{b}contact.html">Start a<br>project &rarr;</a>

    <div class="footer-cols">
      <div>
        <h3>Studio</h3>
        <ul><li>New York, NY</li><li>By appointment</li></ul>
      </div>
      <div>
        <h3>Contact</h3>
        <ul><li><a href="mailto:acestudios.r@gmail.com">acestudios.r@gmail.com</a></li></ul>
      </div>
      <div>
        <h3>Elsewhere</h3>
        <ul><li><a href="https://www.instagram.com/acestudios.ny/" rel="me noopener" target="_blank">Instagram | @acestudios.ny</a></li></ul>
      </div>
      <div>
        <h3>Index</h3>
        <ul><li><a href="{b}work.html">Work</a></li><li><a href="{b}studio.html">Studio</a></li><li><a href="{b}journal.html">Journal</a></li></ul>
      </div>
    </div>

    <div class="colophon">
      <span>&copy; <span data-year>2025</span> Ace Studios</span>
      <span data-clock>-</span>
      <span>Set in Helvetica &amp; Times</span>
    </div>
  </div>
</footer>

<script src="{b}assets/js/background.js"></script>
<script src="{b}assets/js/main.js"></script>
</body>
</html>
'''


# --------------------------------------------------------------- helpers

def esc(text):
    """Escape a plain-text field for HTML.

    title / sub / client / sector / services / deliverables are stored as plain
    text and escaped here. lede / body / quote are treated as trusted HTML so
    you can use entities and inline markup in your copy.
    """
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def load():
    if not os.path.exists(DATA):
        return []
    with open(DATA) as fh:
        return json.load(fh)


def save(projects):
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with open(DATA, "w") as fh:
        json.dump(projects, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s or "project"


def cover_of(p):
    return p.get("cover") or f"assets/img/{p['slug']}.svg"


def wide_of(p):
    return p.get("wide") or cover_of(p)


def replace_region(path, start, end, content):
    """Swap whatever sits between two markers. Fails loudly if they are missing."""
    full = os.path.join(ROOT, path)
    src = open(full).read()
    if start not in src or end not in src:
        raise SystemExit(f"{path}: missing build markers {start} / {end}")
    head, rest = src.split(start, 1)
    _, tail = rest.split(end, 1)
    open(full, "w").write(head + start + "\n" + content + "\n" + " " * 4 + end + tail)


# --------------------------------------------------------------- rendering

def fit_bits(p, base):
    """Projects can ask for their artwork to be shown whole rather than cropped."""
    cls = " " + base + "--contain" if p.get("fit") == "contain" else ""
    bg = ' style="background:%s"' % esc(p["bg"]) if p.get("bg") else ""
    return cls, bg


def card(p, depth=0, wide=False):
    b = "../" * depth
    src = wide_of(p) if wide else cover_of(p)
    cls = "card card--wide" if wide else "card"
    tags = " ".join(p.get("tags", []))
    fcls, fbg = fit_bits(p, "card__frame")
    return f'''      <a class="{cls} reveal" href="{b}work/{p['slug']}.html" data-tags="{esc(tags)}">
        <span class="card__frame{fcls}"{fbg}><img src="{b}{src}" alt="{esc(p['title'])} | {esc(p.get('sub', 'project'))}" loading="lazy"><span class="card__tag">{esc(p.get('sub', ''))}</span></span>
        <span class="card__meta"><span><span class="card__title">{esc(p['title'])}</span><span class="card__sub">{esc(p.get('sub', ''))}</span></span><span class="card__year">{esc(p.get('year', ''))}</span></span>
      </a>'''


def spec_rows(p):
    rows = [("Client", p.get("client")), ("Sector", p.get("sector")),
            ("Year", p.get("year")), ("Services", p.get("services")),
            ("Deliverables", p.get("deliverables"))]
    out = [f'          <div class="spec"><dt>{k}</dt><dd>{v}</dd></div>'
           for k, v in ((k, esc(v)) for k, v in rows if v)]
    return "\n".join(out)


def plate_media(pl, prefix="../"):
    """A plate holds a still, or a silent looping video with a poster frame.

    Two sources are emitted when both exist. MP4 goes first because it is the
    smaller file for browsers that can take it; WebM covers the ones that
    cannot decode H.264 at all.
    """
    alt = esc(pl.get("caption", ""))
    if not pl.get("video"):
        return '<img src="%s%s" alt="%s" loading="lazy">' % (prefix, pl["src"], alt)

    poster = ' poster="%s%s"' % (prefix, pl["poster"]) if pl.get("poster") else ""
    webm = pl["video"].rsplit(".", 1)[0] + ".webm"
    srcs = []
    for path, mime in ((pl["video"], "video/mp4"), (webm, "video/webm")):
        if os.path.exists(os.path.join(ROOT, path)):
            srcs.append('<source src="%s%s" type="%s">' % (prefix, path, mime))
    return ('<video%s autoplay muted loop playsinline preload="auto" aria-label="%s">'
            % (poster, alt)) + "".join(srcs) + "</video>"


def project_page(p, nxt):
    pcls, pbg = fit_bits(p, "plate")
    paras = "\n          ".join(f"<p>{para}</p>" for para in p.get("body", []))
    prose = f'''      <div style="grid-column: 6 / span 7" class="reveal prose" data-delay="80">
          {paras}
      </div>''' if paras else ""

    quote = ""
    if p.get("quote"):
        quote = f'''
  <section class="wrap section--tight">
    <div class="grid">
      <div style="grid-column: 3 / span 8" class="reveal">
        <p class="pull">&ldquo;{p['quote']}&rdquo;</p>
      </div>
    </div>
  </section>
'''

    # Extra images, added whenever you upload the next batch for this project.
    plates = p.get("plates", [])
    plate_block = ""
    if plates:
        cells = "\n".join(
            f'''      <div class="plate{pcls}{' plate--full' if pl.get('full') else ''} reveal"{' data-delay="90"' if i % 2 else ''}{pbg}>{plate_media(pl)}<p class="plate__cap">{pl.get('caption', '')}</p></div>'''
            for i, pl in enumerate(plates))
        plate_block = f'''
  <section class="wrap section--tight">
    <div class="work-grid work-grid--feature">
{cells}
    </div>
  </section>
'''

    nxt_block = ""
    if nxt:
        nxt_block = f'''
  <section class="wrap section rule-top" style="margin-top: clamp(40px,6vw,80px)">
    <p class="eyebrow reveal">Next project</p>
    <a class="reveal" data-delay="60" href="{nxt['slug']}.html" style="display:block; margin-top:14px">
      <span class="h2" style="display:block">{esc(nxt['title'])} &rarr;</span>
      <span class="card__sub" style="display:block; margin-top:10px">{esc(nxt.get('sub', ''))} | {esc(nxt.get('year', ''))}</span>
    </a>
  </section>
'''

    body = f'''
  <section class="wrap project-hero">
    <p class="eyebrow reveal"><a href="../work.html">Work</a> / {esc(p.get('sub', ''))}</p>
    <h1 class="display reveal" data-delay="60" style="margin-top:18px">{esc(p['title'])}</h1>
    <div class="grid" style="margin-top: clamp(28px,5vw,52px)">
      <div style="grid-column: 1 / span 7" class="reveal" data-delay="120">
        <p class="lede">{p.get('lede', '')}</p>
      </div>
    </div>
  </section>

  <section class="wrap">
    <div class="plate{pcls} reveal"{pbg}>
      <img src="../{wide_of(p)}" alt="{esc(p['title'])} | key image">
    </div>
  </section>

  <section class="wrap section">
    <div class="grid">
      <div style="grid-column: 1 / span 4" class="reveal">
        <dl class="spec-grid" style="grid-template-columns: 1fr">
{spec_rows(p)}
        </dl>
      </div>
{prose}
    </div>
  </section>
{quote}{plate_block}{nxt_block}'''

    b = "../"
    desc = (p.get("lede") or f"{p['title']} | {p.get('sub', '')}").replace('"', "'")
    html = HEAD.format(title=esc(f"{p['title']} | Ace Studios"), desc=esc(desc), b=b) + body + FOOT.format(b=b)
    out = os.path.join(ROOT, "work", f"{p['slug']}.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(html)


def build():
    projects = load()
    if not projects:
        print("content/projects.json is empty - nothing to build.")
        return

    # newest first, so the grid reorders itself as you add work
    projects.sort(key=lambda p: (str(p.get("year", "")), p.get("title", "")), reverse=True)

    known = {p["slug"] for p in projects}
    for i, p in enumerate(projects):
        project_page(p, projects[(i + 1) % len(projects)] if len(projects) > 1 else None)

    replace_region("work.html", GRID_START, GRID_END,
                   "\n".join(card(p) for p in projects))

    marked = [p for p in projects if p.get("featured")]
    featured = marked[:2]
    if len(marked) > 2:
        skipped = ", ".join(p["slug"] for p in marked[2:])
        print(f"note: the home page shows 2 featured projects; not shown: {skipped}")
    replace_region("index.html", FEAT_START, FEAT_END,
                   "\n".join(card(p, wide=True) for p in featured))

    # everything not already featured above, newest first
    shown = {p["slug"] for p in featured}
    recent = [p for p in projects if p["slug"] not in shown][:RECENT_COUNT]
    replace_region("index.html", RECENT_START, RECENT_END,
                   "\n".join(card(p) for p in recent))

    # drop pages for projects that are no longer in the data file
    for f in os.listdir(os.path.join(ROOT, "work")):
        if f.endswith(".html") and f[:-5] not in known:
            os.remove(os.path.join(ROOT, "work", f))
            print(f"removed stale page work/{f}")

    # keep the count on work.html honest
    wpath = os.path.join(ROOT, "work.html")
    w = open(wpath).read()
    w = re.sub(r'(<span data-count>)\d+(</span>)', rf'\g<1>{len(projects):02d}\g<2>', w)
    open(wpath, "w").write(w)

    print(f"built {len(projects)} projects: {len(featured)} featured + {len(recent)} recent on the home page")


# --------------------------------------------------------------- commands

def cmd_add():
    projects = load()

    def ask(label, default=""):
        val = input(f"{label}{f' [{default}]' if default else ''}: ").strip()
        return val or default

    print("\nNew project - press Enter to skip anything you do not have yet.\n")
    title = ask("Project / client name")
    if not title:
        raise SystemExit("A name is required.")
    slug = ask("URL slug", slugify(title))
    if any(p["slug"] == slug for p in projects):
        raise SystemExit(f"'{slug}' already exists. Use a different slug, or edit content/projects.json.")

    print(f"\nTags, space separated. Options: {' '.join(TAGS)}")
    p = {
        "slug": slug,
        "title": title,
        "sub": ask("Discipline line (e.g. Brand identity)"),
        "year": ask("Year"),
        "tags": ask("Tags").split(),
        "featured": ask("Feature on the home page? y/N", "n").lower().startswith("y"),
        "cover": ask("Card image path (4:5 crop)", f"assets/img/{slug}.jpg"),
        "wide": ask("Wide hero image path (16:10)", f"assets/img/{slug}-wide.jpg"),
        "client": ask("Client"),
        "sector": ask("Sector"),
        "services": ask("Services"),
        "deliverables": ask("Deliverables"),
        "lede": ask("One-line summary"),
        "body": [],
        "quote": "",
        "plates": [],
    }
    print("\nDescription paragraphs - blank line to finish.")
    while True:
        line = input("  > ").strip()
        if not line:
            break
        p["body"].append(line)

    projects.append(p)
    save(projects)
    print(f"\nAdded '{title}' to content/projects.json")

    missing = [k for k in ("cover", "wide") if not os.path.exists(os.path.join(ROOT, p[k]))]
    if missing:
        print("Drop these image files in before the page will look right:")
        for k in missing:
            print(f"  {p[k]}")
    build()


def cmd_list():
    projects = load()
    if not projects:
        print("No projects yet.")
        return
    for p in sorted(projects, key=lambda x: str(x.get("year", "")), reverse=True):
        flags = []
        if p.get("featured"):
            flags.append("featured")
        if p.get("demo"):
            flags.append("DEMO")
        for k in ("cover", "wide"):
            if p.get(k) and not os.path.exists(os.path.join(ROOT, p[k])):
                flags.append(f"missing {k}")
        tail = f"  [{', '.join(flags)}]" if flags else ""
        print(f"  {p.get('year', '----')}  {p['slug']:<22} {p['title']}{tail}")


def cmd_drop(slugs, demo_only=False):
    projects = load()
    if demo_only:
        keep = [p for p in projects if not p.get("demo")]
    else:
        keep = [p for p in projects if p["slug"] not in slugs]
    dropped = len(projects) - len(keep)
    if not dropped:
        print("Nothing matched.")
        return
    save(keep)
    print(f"removed {dropped} project(s)")
    build()


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        build()
    elif args[0] == "add":
        cmd_add()
    elif args[0] == "list":
        cmd_list()
    elif args[0] == "drop-demo":
        cmd_drop([], demo_only=True)
    elif args[0] == "drop":
        cmd_drop(args[1:])
    else:
        raise SystemExit(__doc__)
