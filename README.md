# Ace Studios

Marketing site for Ace Studios, a graphic design practice. Static HTML, CSS and
vanilla JavaScript — no build step, no dependencies, no framework. Open
`index.html` in a browser and it works.

The visual direction is editorial-minimal in the vein of contemporary
film/culture studio sites: near-black ground, oversized grotesk headlines,
monospace metadata, a hairline grid, and desaturated cover plates that come to
colour on hover. All artwork and copy in this repo are original.

## Structure

```
index.html            Home — hero, ticker, featured work, capabilities
work.html             Work index with discipline filters
work/*.html           Eight project case studies
studio.html           About, process, team, recognition
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

## Editing

**Colour, type and spacing** live as custom properties at the top of
`assets/css/main.css` (`--ink`, `--paper`, `--accent`, `--gutter`, …). Changing
`--accent` re-skins every hover state, tag and rule on the site.

**Adding a project:** copy an existing file in `work/`, then add a card to
`work.html` (and `index.html` if it should be featured). The card's
`data-tags` attribute drives the filter buttons — use the same keys as the
`data-filter` values (`identity packaging editorial digital campaign motion`).

**Cover plates:** `tools/make_art.py` generates each project's 4:5 and 16:10
SVG plates from a seeded geometric composition. Edit the `PROJECTS` list —
slug, composition (`arcs`, `letter`, `waves`, `stripes`, `blocks`, `halftone`,
`grid`, `rings`) and a three-colour palette — then run:

```sh
python3 tools/make_art.py
```

Replacing a plate with a real photograph is just swapping the file in
`assets/img/`; cards crop to 4:5 and detail plates to 16:10.

## Notes

- Scroll reveals are gated behind a `.js` class on `<html>`, so the site stays
  fully readable with JavaScript disabled or blocked.
- `prefers-reduced-motion` disables the reveals, the marquee and smooth scroll.
- The contact form has no backend; it composes a `mailto:` handoff. Point it at
  a form service (Formspree, Basin, a serverless function) before launch — see
  the `data-contact-form` handler in `assets/js/main.js`.
- Placeholder details to replace before launch: the studio address, phone
  number, email domain, social links, team names and the client work itself.

## Deploying

Any static host. For GitHub Pages: Settings → Pages → deploy from branch, root
directory. No configuration needed.
