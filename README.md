# Ace Studios

Marketing site for Ace Studios, a one-person graphic design practice in New
York — logos and brand identity, clothing and merch graphics, advertising, web
design, typography and print. Static HTML, CSS and
vanilla JavaScript — no dependencies, no framework. Open `index.html` in a
browser and it works, and it deploys as-is to any static host.

There is a small Python script for authoring (`tools/build.py`) that renders the
work section from a data file, so adding a project does not mean editing markup
by hand. It is a convenience for you, not a build step for deployment — what is
committed is the finished HTML.

The visual direction is editorial-minimal in the vein of contemporary
film/culture studio sites: near-black ground, oversized grotesk headlines,
monospace metadata, a hairline grid, and desaturated cover plates that come to
colour on hover. All artwork and copy in this repo are original.

## Structure

```
content/projects.json The work, as data — this is what you edit
tools/build.py        Renders the work section from that data
index.html            Home — hero, ticker, featured work, capabilities
work.html             Work index with discipline filters
work/*.html           One page per project (generated — do not hand-edit)
studio.html           About, process, team
services.html         Five disciplines + engagement models
journal.html          Writing index + newsletter signup
contact.html          Enquiry form and direct contacts
404.html              Not-found page
assets/css/main.css   Whole design system (tokens at the top)
assets/js/main.js     Nav, scroll reveal, filters, marquee, form handling
assets/img/*.svg      Generated cover plates
tools/make_art.py     Regenerates the cover plates
```

## Local preview

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

A plain file:// open works too, but a server is closer to production.

## Adding work

Projects live in `content/projects.json`. You never hand-edit the work markup —
add the data, drop the images in, and run the build. Do it a project at a time,
whenever you have one ready.

```sh
python3 tools/build.py add     # answer the prompts (Enter skips anything)
python3 tools/build.py         # re-render after editing projects.json by hand
python3 tools/build.py list    # what is published, and which images are missing
python3 tools/build.py drop <slug>
python3 tools/build.py drop-demo   # delete every remaining demo project
```

The build writes `work/<slug>.html` for each project, refreshes the grid on
`work.html` and the featured cards on `index.html`, updates the project count,
and deletes pages for projects no longer in the data file. Everything else —
studio, services, journal, contact — is hand-edited and never touched.

### Images

Put them in `assets/img/` and point the project at them:

| Field    | Used for              | Shape                              |
|----------|-----------------------|------------------------------------|
| `cover`  | the card in the grid  | cropped to 4:5, any source size    |
| `wide`   | the page's key image  | full width, 16:10 reads best       |
| `plates` | extra images below    | cropped to 4:5, two per row        |

Cards crop with `object-fit: cover`, so an off-ratio photo still sits correctly.
If you only have one image, set `cover` and leave `wide` out — it falls back.

`plates` is how you add work in passes: ship a project with one image, then add
more later and re-run the build.

```json
"plates": [
  { "src": "assets/img/client-detail.jpg", "caption": "Fig. 02 — Packaging" }
]
```

### Fields

`title`, `sub`, `year`, `client`, `sector`, `services`, `deliverables` are plain
text — write `&` not `&amp;`, the build escapes them. `lede`, `body` and `quote`
are treated as HTML so you can use entities and inline markup. Blank fields are
skipped rather than rendered empty, so a sparse project still looks deliberate.

`tags` drives the filter buttons: `identity apparel advertising web typography
print`. `featured: true` puts a project on the home page — the two newest
featured projects are shown.

### Cover plates for projects without photography

`tools/make_art.py` generates abstract geometric SVG plates. Edit its `PROJECTS`
list — slug, composition (`arcs`, `letter`, `waves`, `stripes`, `blocks`,
`halftone`, `grid`, `rings`) and a three-colour palette — then run
`python3 tools/make_art.py`. The demo projects use these.

## Design

Colour, type and spacing are custom properties at the top of
`assets/css/main.css` (`--ink`, `--paper`, `--accent`, `--gutter`, …). Changing
`--accent` re-skins every hover state, tag and rule on the site.

### The moving background

`assets/js/background.js` draws a canvas field behind the whole site: soft
colour blobs and crisp dots, each on its own depth layer. They move against the
scroll, drift slowly on their own, and ease away from the cursor.

Everything is tuned in the `SETTINGS` object at the top of that file:

| Setting | What it does |
|---------------------|-------------------------------------------------|
| `parallax` | how hard the field moves against scroll; `0` pins it still |
| `drift` | idle movement when nothing is happening |
| `pointerRadius` | how close the cursor gets before dots react |
| `pointerPush` | how far the cursor shoves a dot |
| `dotAlpha` | `[min, max]` dot opacity |
| `blobAlpha` | colour-field opacity — raise carefully, this is what muddies type |
| `maxDots` | ceiling on dot count |

It is deliberately faint: on a portfolio the background must lose to the work.
If you turn `blobAlpha` up much past `0.1` the colour starts washing over the
headlines and the type stops looking crisp.

To switch it off for one page, put `data-bg="off"` on that page's `<html>` tag.

It looks after itself in a few ways: the blob sprites are rendered once and
blitted rather than rebuilt every frame, the loop pauses when the tab is hidden,
dot count scales down on phones, cursor tracking is skipped for touch so it
never fights scrolling, and `prefers-reduced-motion` paints a single static
frame instead of animating. With JavaScript off the canvas simply never
appears and the site looks exactly as it did before.

## Notes

- Scroll reveals are gated behind a `.js` class on `<html>`, so the site stays
  fully readable with JavaScript disabled or blocked.
- `prefers-reduced-motion` disables the reveals, the marquee and smooth scroll.
- The contact form has no backend; it composes a `mailto:` handoff. Point it at
  a form service (Formspree, Basin, a serverless function) before launch — see
  the `data-contact-form` handler in `assets/js/main.js`.
- Contact details are live: acestudios.r@gmail.com and @acestudios.ny. No
  street address is published anywhere on the site.
- The site is written as a one-person practice that brings in collaborators per
  project. Services lead with logos, clothing graphics and advertising, then web,
  typography and print.
- Still placeholder: the eight demo projects (`tools/build.py drop-demo`), the
  journal posts, and your name — `studio.html` has a comment marking where it
  goes. The Recognition section and the home-page stats row are commented out
  rather than filled with invented figures. `services.html` describes fixed-price
  quoting instead of listing rates; there is a comment where rates would go.
- `404.html` links to `/work.html` root-absolute. That is right for a custom
  domain; on a GitHub Pages project subpath it needs the repo prefix.

## Deploying

Any static host. For GitHub Pages: Settings → Pages → deploy from branch, root
directory. No configuration needed.
