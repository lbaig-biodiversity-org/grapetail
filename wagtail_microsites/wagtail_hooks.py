"""
Wagtail hooks for the Microsite Builder.

- Registers the custom static assets needed by the GrapesJS admin panel.
- Wires the MicrositeBuilderPanel into the Wagtail admin.
"""

from wagtail import hooks
from django.templatetags.static import static
from django.utils.html import format_html


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        '<script src="{}"></script>',
        static("wagtail_microsites/js/microsite-builder.js"),
    )


@hooks.register("insert_editor_css")
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("wagtail_microsites/css/microsite-builder.css"),
    )
