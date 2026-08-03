"""
Wagtail hooks for the Microsite Builder.

- Registers the custom static assets needed by the GrapesJS admin panel.
- Injects GrapesJS (from CDN) and our custom builder script/styles.
"""

from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from wagtail import hooks

# GrapesJS 0.21.x from jsDelivr CDN — loaded before our builder script.
_GRAPES_JS_CDN = "https://cdn.jsdelivr.net/npm/grapesjs@0.21.13/dist/grapes.min.js"
_GRAPES_CSS_CDN = "https://cdn.jsdelivr.net/npm/grapesjs@0.21.13/dist/css/grapes.min.css"


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        '<script src="{cdn}" crossorigin="anonymous"></script>'
        '<script src="{local}"></script>',
        cdn=_GRAPES_JS_CDN,
        local=static("wagtail_microsites/js/microsite-builder.js"),
    )


@hooks.register("insert_editor_css")
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{cdn}" crossorigin="anonymous">'
        '<link rel="stylesheet" href="{local}">',
        cdn=_GRAPES_CSS_CDN,
        local=static("wagtail_microsites/css/microsite-builder.css"),
    )
