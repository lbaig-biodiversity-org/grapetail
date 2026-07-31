"""
Template tags for the Wagtail Microsite Builder.

Load with: {% load wagtail_microsites_tags %}
"""

from __future__ import annotations

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from wagtail_microsites.sanitizers import sanitize_url, sanitize_rich_text as _sanitize_rt

register = template.Library()


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


@register.filter(name="safe_url", is_safe=True)
def safe_url_filter(value: str | None) -> str:
    """Return the URL only if it uses an allowed scheme, else ''."""
    return sanitize_url(value)


@register.filter(name="sanitize_rich_text", is_safe=True)
def sanitize_rich_text_filter(value: str | None):
    """Sanitise HTML for safe output in rich_text blocks."""
    return mark_safe(_sanitize_rt(value))


@register.filter(name="column_widths")
def column_widths_filter(ratio: str | None) -> tuple[str, str]:
    """
    Convert a two-part ratio string ("40/60") into a tuple of CSS fr values.

    Returns ("1fr", "1fr") for any invalid input.
    """
    if not ratio:
        return ("1fr", "1fr")
    parts = ratio.split("/")
    if len(parts) != 2:
        return ("1fr", "1fr")
    try:
        a, b = int(parts[0]), int(parts[1])
    except ValueError:
        return ("1fr", "1fr")
    # Express as fractional units
    return (f"{a}fr", f"{b}fr")


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


@register.simple_tag(takes_context=False, name="render_block")
def render_block_tag(block: dict) -> str:
    """
    Render a single block dict through its template.

    Used in nested column templates to render sub-blocks.

    Usage: {% render_block sub_block %}
    """
    block_type = block.get("type", "")
    template_name = f"wagtail_microsites/blocks/{block_type}.html"
    try:
        rendered = render_to_string(
            template_name,
            {"block": block, "props": block.get("props", {})},
        )
    except Exception:
        rendered = f"<!-- unknown block type: {block_type} -->"
    return mark_safe(rendered)
