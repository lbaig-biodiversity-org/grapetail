# grapetail

A Wagtail-based project with a constrained visual microsite builder.

---

## Overview

**grapetail** extends Wagtail with a `wagtail_microsites` app that lets editors
build short-lived campaign microsites from a curated library of approved blocks.
The visual editor is powered by GrapesJS acting as a constrained drag-and-drop
shell — **not** an arbitrary HTML editor. The canonical content representation
is a validated JSON schema; all rendering is done server-side through Django
templates.

This is **Pattern B** architecture:

```
Editor → GrapesJS UI → Approved JSON schema → Server-side template rendering
                              ↑ validated, not raw HTML
```

---

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Apply migrations

```bash
python manage.py migrate
```

### 3. Create a superuser and start the development server

```bash
python manage.py createsuperuser
python manage.py runserver
```

### 4. Create a Microsite page

1. Go to `/admin/` and log in.
2. In the Wagtail page tree, add a child page of type **Microsite page** under
   any parent.
3. Fill in the title, optional theme, and optional expiry date.
4. Use the visual builder panel (GrapesJS) to compose the page from approved
   blocks, or edit the `builder_json` field directly for development.
5. Publish and visit the page URL.

---

## Architecture

### App structure

```
wagtail_microsites/
  apps.py                    — AppConfig
  models.py                  — MicrositePage
  schema.py                  — BLOCK_SCHEMA registry + validate_builder_payload()
  sanitizers.py              — URL and HTML sanitisation helpers
  wagtail_hooks.py           — Registers admin JS/CSS
  templatetags/
    wagtail_microsites_tags.py — safe_url, sanitize_rich_text, column_widths, render_block
  templates/
    wagtail_microsites/
      pages/
        microsite_page.html  — Public page template
      blocks/
        hero.html
        cta_band.html
        quote.html
        two_column.html
        three_column.html
        card.html
        rich_text.html
        donation_embed.html
        alert_banner.html
        faq.html
  static/
    wagtail_microsites/
      js/
        microsite-builder.js — GrapesJS integration + schema serialiser
      css/
        microsite-builder.css — Admin panel styles
        microsite-public.css  — Public-facing component styles
  tests/
    test_schema.py           — Schema validation tests
    test_rendering.py        — Rendering and security tests
```

### Data model

`MicrositePage` (extends Wagtail `Page`) stores:

| Field | Type | Purpose |
|---|---|---|
| `theme` | CharField | Brand theme variant (CSS class hook) |
| `expires_at` | DateTimeField | Optional expiry; pages flag themselves as expired |
| `builder_json` | JSONField | **Canonical content** — validated block schema |
| `rendered_preview` | TextField | Pre-rendered HTML cache, regenerated on save |

The `builder_json` field stores a structure like:

```json
{
  "version": 1,
  "blocks": [
    {
      "type": "hero",
      "props": {
        "headline": "Save the Wetlands",
        "subheadline": "Act now to protect biodiversity",
        "cta_text": "Donate",
        "cta_url": "https://example.org/donate",
        "overlay_heading_level": "h1",
        "overlay_font_weight": "extrabold",
        "overlay_font_size": "3rem",
        "overlay_text_color": "#ffffff",
        "overlay_horizontal_align": "center",
        "overlay_vertical_align": "center"
      }
    },
    {
      "type": "quote",
      "props": {
        "text": "We cannot wait.",
        "attribution": "Campaign Lead"
      }
    }
  ]
}
```

---

## Approved block types

### `hero`

Full-width banner with a background image and overlay text.

| Prop | Required | Values |
|---|---|---|
| `headline` | ✅ | string |
| `subheadline` | | string |
| `background_image_url` | | https/http URL |
| `cta_text` | | string |
| `cta_url` | | https/http URL |
| `overlay_heading_level` | | `h1` `h2` `h3` `h4` |
| `overlay_font_weight` | | `normal` `semibold` `bold` `extrabold` |
| `overlay_font_size` | | CSS value: `2rem`, `48px`, etc. |
| `overlay_font_family` | | CSS font-family string |
| `overlay_text_color` | | CSS color |
| `overlay_horizontal_align` | | `left` `center` `right` |
| `overlay_vertical_align` | | `top` `center` `bottom` |

### `cta_band`

High-contrast call-to-action strip.

| Prop | Required | Notes |
|---|---|---|
| `headline` | ✅ | |
| `cta_text` | ✅ | |
| `cta_url` | ✅ | https/http only |
| `body` | | |
| `background_color` | | CSS color |
| `text_color` | | CSS color |

### `quote`

Styled blockquote.

| Prop | Required | Notes |
|---|---|---|
| `text` | ✅ | |
| `attribution` | | |
| `source_url` | | https/http/mailto/tel only |

### `two_column`

Two-column grid with adjustable ratio.

| Prop | Required | Notes |
|---|---|---|
| `ratio` | | `50/50` `40/60` `67/33` etc. (default `50/50`) |
| `gap` | | CSS gap value (default `2rem`) |
| `stack_on_mobile` | | boolean (default `true`) |
| `left_blocks` | | list of sub-blocks |
| `right_blocks` | | list of sub-blocks |

Sub-blocks can be any approved block type.

### `three_column`

Three-column equal grid.

| Prop | Required | Notes |
|---|---|---|
| `gap` | | CSS gap value (default `2rem`) |
| `stack_on_mobile` | | boolean |
| `col1_blocks` / `col2_blocks` / `col3_blocks` | | lists of sub-blocks |

### `card`

Self-contained content card with optional image and CTA.

| Prop | Required | Notes |
|---|---|---|
| `title` | ✅ | |
| `body` | | plain text |
| `image_url` | | https/http only |
| `image_alt` | | |
| `cta_text` | | |
| `cta_url` | | https/http only |

### `rich_text`

Sanitised HTML block. Images are automatically sized to the full column width.

| Prop | Required | Notes |
|---|---|---|
| `body` | ✅ | HTML; sanitised server-side via bleach |

### `donation_embed`

Donation or sign-up embed via iframe or inline form ID.

| Prop | Required | Notes |
|---|---|---|
| `embed_type` | ✅ | `donation` `signup` `email` |
| `embed_url` | | https/http only; rendered as sandboxed iframe |
| `form_id` | | inline form identifier |
| `title` | | visible heading |
| `description` | | supporting text |

### `alert_banner`

Dismissible or permanent alert strip.

| Prop | Required | Notes |
|---|---|---|
| `message` | ✅ | |
| `level` | | `info` `warning` `success` `error` |
| `dismissible` | | boolean |
| `cta_text` / `cta_url` | | optional action link |

### `faq`

Accessible accordion-style FAQ.

| Prop | Required | Notes |
|---|---|---|
| `items` | ✅ | list of `{question, answer}` objects |
| `headline` | | section heading |

---

## Adding a new block type

1. **Register the schema** in `wagtail_microsites/schema.py` — add an entry to
   `BLOCK_SCHEMA` with `required`, `optional`, `nested`, and `validators` keys.

2. **Create a template** at
   `wagtail_microsites/templates/wagtail_microsites/blocks/<type>.html`.
   The template receives `{{ props }}` (the block's props dict) and
   `{{ block }}` (the full block dict).
   Load `{% load wagtail_microsites_tags %}` for helper filters.

3. **Add GrapesJS component** in
   `wagtail_microsites/static/wagtail_microsites/js/microsite-builder.js` —
   add an entry to `BLOCK_DEFS` with `label`, `category`, `defaultProps`, and
   `traits`.

4. **Write tests** — add cases to `wagtail_microsites/tests/test_schema.py`
   covering required/optional/unknown props and any validators.
   Add rendering tests to `test_rendering.py` if the block has non-trivial
   template logic.

5. Run `python manage.py test wagtail_microsites` to verify.

---

## Security

- **Schema validation** — only approved block types and approved prop names are
  accepted. Unknown props raise `MicrositeSchemaError`.
- **URL sanitisation** — all URL props are validated; only `https`, `http`,
  `mailto`, and `tel` schemes are allowed. `javascript:` and `data:` URLs are
  rejected at schema validation time and again at render time.
- **HTML sanitisation** — `rich_text` block content is passed through
  `bleach.clean()` with an explicit allowlist of tags and attributes. Event
  handlers (`onclick`, `onload`, etc.), `style` attributes, and `javascript:`
  hrefs are stripped.
- **No arbitrary JS** — GrapesJS is configured to expose only approved
  components. The saved artifact is structured JSON, not raw HTML/CSS.
- **Sandboxed iframes** — `donation_embed` iframes use
  `sandbox="allow-forms allow-same-origin allow-popups"` to limit script
  execution.
- **Template rendering** — all page output is controlled by Django templates.
  Editors cannot inject arbitrary markup or scripts.

---

## Themes

Set the `theme` field to apply a CSS class (`microsite--theme-<value>`) to the
page wrapper. Add theme styles in `microsite-public.css`. Built-in variants:

- `default` — base styles
- `campaign` — red accent, taller hero
- `minimal` — darker overlay

---

## Running tests

```bash
python manage.py test wagtail_microsites
```

---

## What's complete vs. what's next

### ✅ Complete in this PR

- `MicrositePage` model with theme, expiry, builder JSON, and pre-rendered cache
- Full schema validation for all 10 approved block types with per-prop validators
- Server-side rendering via Django block templates
- All 10 block templates: hero, CTA band, quote, two-column, three-column,
  card, rich text, donation embed, alert banner, FAQ
- Hero overlay text with designable heading level, font weight, font size, font
  family, colour, horizontal alignment, and vertical position
- Two-column block with adjustable ratio (50/50, 40/60, 67/33, etc.)
- GrapesJS admin integration scaffold (constrained block UI, schema
  serialisation, canvas preview)
- Public CSS for all components with responsive stacking for column blocks
- Admin CSS for the builder panel
- 85 passing tests covering schema validation, rendering, and security
- URL and HTML sanitisation layer
- README with full documentation

### 🔜 Recommended follow-up work

- **GrapesJS polish** — inline trait editing, live preview in canvas, device
  preview toggle, drag-and-drop reorder
- **Nested block editing** — UI for editing sub-blocks inside two-column /
  three-column containers
- **Page templates / presets** — allow editors to clone from a set of
  pre-built microsite layouts
- **Wagtail image picker** — replace raw URL inputs with the Wagtail image
  chooser for `image_url` props
- **Expiry workflow** — scheduled task to auto-unpublish expired microsites
- **Analytics** — per-microsite UTM / pixel configuration
- **Accessibility linting** — heading structure, colour contrast checks on save
- **More themes** — extend the theme system with a design token approach
