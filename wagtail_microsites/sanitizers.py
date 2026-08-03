"""
URL and content sanitisation helpers for the microsite builder.

These are used during rendering, not just at save time, so that any
content that slips through validation is still rendered safely.
"""

from __future__ import annotations

import html
import re
from urllib.parse import urlparse

import bleach

# ---------------------------------------------------------------------------
# URL sanitisation
# ---------------------------------------------------------------------------

_SAFE_SCHEMES = {"https", "http", "mailto", "tel"}


def sanitize_url(url: str | None) -> str:
    """Return the URL if it uses an allowed scheme, else ''."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return ""
    if parsed.scheme not in _SAFE_SCHEMES:
        return ""
    return url.strip()


# ---------------------------------------------------------------------------
# Rich-text / HTML sanitisation
# ---------------------------------------------------------------------------

# Tags and attributes that are safe in rich-text blocks.
_ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "s", "del",
    "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "blockquote", "pre", "code",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "figure", "figcaption",
    "hr", "sub", "sup",
]

# Explicitly block all event handler attributes
_EVENT_HANDLER_PREFIX = "on"

# Attributes that are explicitly allowed (not event handlers, not URL attrs handled separately)
_SAFE_ATTRS: dict[str, set[str]] = {
    "a": {"href", "title", "rel", "target"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
    "table": {"class"},
    "th": {"scope", "colspan", "rowspan"},
    "td": {"colspan", "rowspan"},
    "*": {"class", "id"},
}

# Attributes whose values are URLs and must pass sanitize_url()
_URL_ATTRS: set[str] = {"href", "src", "action", "formaction"}


def _clean_url_attr(tag: str, name: str, value: str) -> str | bool:
    # Immediately block any event handler attribute (onclick, onload, etc.)
    if name.lower().startswith(_EVENT_HANDLER_PREFIX) and name.lower() != "on":
        return False
    # Also block common unsafe attributes by name
    if name.lower() in {"style", "formaction", "action", "data", "srcdoc", "xlink:href"}:
        return False

    # Validate URL attributes
    if name in _URL_ATTRS:
        cleaned = sanitize_url(value)
        return cleaned if cleaned else False

    # For rel/target attributes on <a>
    if tag == "a" and name == "target":
        return value if value in ("_blank", "_self", "_parent", "_top") else False
    if tag == "a" and name == "rel":
        # Allow only safe rel values
        allowed_rel = {"noopener", "noreferrer", "nofollow", "ugc", "sponsored"}
        parts = [p.strip() for p in value.split()]
        return " ".join(p for p in parts if p in allowed_rel) or False

    # Check against the allow-list
    tag_allowed = _SAFE_ATTRS.get(tag, set()) | _SAFE_ATTRS.get("*", set())
    return name in tag_allowed


def sanitize_rich_text(html_content: str | None) -> str:
    """
    Sanitise HTML from a rich_text block.

    - Only allowed tags/attributes are kept.
    - URLs in href/src are restricted to safe schemes.
    - Returns '' for None / empty.
    """
    if not html_content:
        return ""
    return bleach.clean(
        html_content,
        tags=_ALLOWED_TAGS,
        attributes=_clean_url_attr,
        strip=True,
    )


# ---------------------------------------------------------------------------
# Plain-text sanitisation (used for e.g. embed titles/descriptions)
# ---------------------------------------------------------------------------


def sanitize_text(text: str | None) -> str:
    """Escape HTML entities from a plain-text value."""
    if not text:
        return ""
    return html.escape(str(text), quote=True)
