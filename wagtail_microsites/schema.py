"""
Approved block schema for the Wagtail Microsite Builder.

Each entry in BLOCK_SCHEMA defines:
  - required: props that must be present and non-empty
  - optional: props that may be present
  - nested: props that contain a list of sub-blocks (validated recursively)
  - validators: mapping of prop name -> callable for extra per-prop validation

Only block types listed here are allowed.  Any unknown prop or block type
causes a MicrositeSchemaError to be raised by validate_builder_payload().
"""

from __future__ import annotations

import re
from typing import Any, Callable
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------


class MicrositeSchemaError(ValueError):
    """Raised when the builder JSON does not conform to the approved schema."""


# ---------------------------------------------------------------------------
# URL / embed helpers
# ---------------------------------------------------------------------------

_SAFE_URL_SCHEMES = {"https", "http", "mailto", "tel"}
_ALLOWED_EMBED_TYPES = {"donation", "signup", "email"}
_ALLOWED_ALERT_LEVELS = {"info", "warning", "success", "error"}
_ALLOWED_HEADING_LEVELS = {"h1", "h2", "h3", "h4"}
_ALLOWED_FONT_WEIGHTS = {"normal", "semibold", "bold", "extrabold"}
_ALLOWED_H_ALIGNS = {"left", "center", "right"}
_ALLOWED_V_ALIGNS = {"top", "center", "bottom"}

# Captures values like "2rem", "24px", "1.5em", "120%"
_FONT_SIZE_RE = re.compile(r"^\d+(\.\d+)?(rem|em|px|vw|%)$")
# Simple CSS font-size guard: allow named sizes too
_NAMED_FONT_SIZES = {"small", "medium", "large", "x-large", "xx-large"}

# Column ratio:  "40/60", "33/34/33", "50/50", etc.
_RATIO_RE = re.compile(r"^\d{1,3}(/\d{1,3})+$")


def _validate_url(value: str, prop: str) -> None:
    try:
        parsed = urlparse(value)
    except Exception:
        raise MicrositeSchemaError(f"'{prop}' is not a valid URL.")
    if parsed.scheme not in _SAFE_URL_SCHEMES:
        raise MicrositeSchemaError(
            f"'{prop}' URL scheme '{parsed.scheme}' is not allowed. "
            f"Allowed: {', '.join(sorted(_SAFE_URL_SCHEMES))}."
        )


def _validate_optional_url(value: str, prop: str) -> None:
    if value:
        _validate_url(value, prop)


def _validate_embed_type(value: str, prop: str) -> None:
    if value not in _ALLOWED_EMBED_TYPES:
        raise MicrositeSchemaError(
            f"'{prop}' must be one of: {', '.join(sorted(_ALLOWED_EMBED_TYPES))}."
        )


def _validate_alert_level(value: str, prop: str) -> None:
    if value and value not in _ALLOWED_ALERT_LEVELS:
        raise MicrositeSchemaError(
            f"'{prop}' must be one of: {', '.join(sorted(_ALLOWED_ALERT_LEVELS))}."
        )


def _validate_heading_level(value: str, prop: str) -> None:
    if value and value not in _ALLOWED_HEADING_LEVELS:
        raise MicrositeSchemaError(
            f"'{prop}' must be one of: {', '.join(sorted(_ALLOWED_HEADING_LEVELS))}."
        )


def _validate_font_weight(value: str, prop: str) -> None:
    if value and value not in _ALLOWED_FONT_WEIGHTS:
        raise MicrositeSchemaError(
            f"'{prop}' must be one of: {', '.join(sorted(_ALLOWED_FONT_WEIGHTS))}."
        )


def _validate_font_size(value: str, prop: str) -> None:
    if value and not (_FONT_SIZE_RE.match(value) or value in _NAMED_FONT_SIZES):
        raise MicrositeSchemaError(
            f"'{prop}' must be a valid CSS font-size (e.g. '2rem', '24px') or a named size."
        )


def _validate_h_align(value: str, prop: str) -> None:
    if value and value not in _ALLOWED_H_ALIGNS:
        raise MicrositeSchemaError(
            f"'{prop}' must be one of: {', '.join(sorted(_ALLOWED_H_ALIGNS))}."
        )


def _validate_v_align(value: str, prop: str) -> None:
    if value and value not in _ALLOWED_V_ALIGNS:
        raise MicrositeSchemaError(
            f"'{prop}' must be one of: {', '.join(sorted(_ALLOWED_V_ALIGNS))}."
        )


def _validate_column_ratio(value: str, prop: str) -> None:
    if not value:
        return
    if not _RATIO_RE.match(value):
        raise MicrositeSchemaError(
            f"'{prop}' must be a slash-separated ratio like '50/50' or '40/60'."
        )
    parts = [int(p) for p in value.split("/")]
    if any(p <= 0 or p > 100 for p in parts):
        raise MicrositeSchemaError(
            f"'{prop}': each ratio segment must be between 1 and 100."
        )


def _validate_boolean(value: Any, prop: str) -> None:
    if not isinstance(value, bool):
        raise MicrositeSchemaError(f"'{prop}' must be a boolean (true/false).")


def _validate_faq_items(value: Any, prop: str) -> None:
    if not isinstance(value, list) or len(value) == 0:
        raise MicrositeSchemaError(f"'{prop}' must be a non-empty list.")
    for i, item in enumerate(value):
        if not isinstance(item, dict):
            raise MicrositeSchemaError(f"'{prop}[{i}]' must be an object.")
        for key in ("question", "answer"):
            if not item.get(key):
                raise MicrositeSchemaError(
                    f"'{prop}[{i}].{key}' is required and must be non-empty."
                )
        unknown = set(item.keys()) - {"question", "answer"}
        if unknown:
            raise MicrositeSchemaError(
                f"'{prop}[{i}]' has unknown keys: {', '.join(sorted(unknown))}."
            )


# ---------------------------------------------------------------------------
# Block schema registry
# ---------------------------------------------------------------------------
#
# Each block definition is a dict with:
#   required  – list[str]
#   optional  – list[str]
#   nested    – list[str]  (props that contain a sub-block list)
#   validators – dict[str, Callable[[str, str], None]]
#
# Nested props are validated recursively but their allowed block types are
# the same full set (so columns can contain any approved block).

BLOCK_SCHEMA: dict[str, dict[str, Any]] = {
    "hero": {
        "required": ["headline"],
        "optional": [
            "subheadline",
            "background_image_url",
            "cta_text",
            "cta_url",
            # Overlay text styling & positioning
            "overlay_heading_level",   # h1-h4
            "overlay_font_weight",     # normal / bold / extrabold
            "overlay_font_size",       # e.g. "2rem"
            "overlay_font_family",     # CSS font-family string
            "overlay_text_color",      # CSS color (validated as non-empty string only)
            "overlay_horizontal_align",  # left / center / right
            "overlay_vertical_align",    # top / center / bottom
        ],
        "nested": [],
        "validators": {
            "background_image_url": _validate_optional_url,
            "cta_url": _validate_optional_url,
            "overlay_heading_level": _validate_heading_level,
            "overlay_font_weight": _validate_font_weight,
            "overlay_font_size": _validate_font_size,
            "overlay_horizontal_align": _validate_h_align,
            "overlay_vertical_align": _validate_v_align,
        },
    },
    "cta_band": {
        "required": ["headline", "cta_text", "cta_url"],
        "optional": ["body", "background_color", "text_color"],
        "nested": [],
        "validators": {
            "cta_url": _validate_url,
        },
    },
    "quote": {
        "required": ["text"],
        "optional": ["attribution", "source_url"],
        "nested": [],
        "validators": {
            "source_url": _validate_optional_url,
        },
    },
    "two_column": {
        "required": [],
        "optional": ["ratio", "gap", "stack_on_mobile"],
        # left_blocks / right_blocks are the sub-block lists
        "nested": ["left_blocks", "right_blocks"],
        "validators": {
            "ratio": _validate_column_ratio,
            "stack_on_mobile": _validate_boolean,
        },
    },
    "three_column": {
        "required": [],
        "optional": ["gap", "stack_on_mobile"],
        "nested": ["col1_blocks", "col2_blocks", "col3_blocks"],
        "validators": {
            "stack_on_mobile": _validate_boolean,
        },
    },
    "card": {
        "required": ["title"],
        "optional": ["body", "image_url", "image_alt", "cta_text", "cta_url"],
        "nested": [],
        "validators": {
            "image_url": _validate_optional_url,
            "cta_url": _validate_optional_url,
        },
    },
    "rich_text": {
        # body is expected to be sanitized HTML (the server sanitizes on render)
        "required": ["body"],
        "optional": [],
        "nested": [],
        "validators": {},
    },
    "donation_embed": {
        "required": ["embed_type"],
        "optional": ["embed_url", "form_id", "title", "description"],
        "nested": [],
        "validators": {
            "embed_type": _validate_embed_type,
            "embed_url": _validate_optional_url,
        },
    },
    "alert_banner": {
        "required": ["message"],
        "optional": ["level", "dismissible", "cta_text", "cta_url"],
        "nested": [],
        "validators": {
            "level": _validate_alert_level,
            "dismissible": _validate_boolean,
            "cta_url": _validate_optional_url,
        },
    },
    "faq": {
        "required": ["items"],
        "optional": ["headline"],
        "nested": [],
        "validators": {
            "items": _validate_faq_items,
        },
    },
}


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------


def _validate_block(block: Any, index: int, prefix: str = "") -> dict[str, Any]:
    """Validate a single block dict and return a normalised copy."""
    if not isinstance(block, dict):
        raise MicrositeSchemaError(f"{prefix}Block {index} must be an object.")

    block_type = block.get("type")
    props = block.get("props", {})

    if block_type not in BLOCK_SCHEMA:
        raise MicrositeSchemaError(
            f"{prefix}Block {index}: unsupported block type '{block_type}'. "
            f"Allowed: {', '.join(sorted(BLOCK_SCHEMA.keys()))}."
        )

    if not isinstance(props, dict):
        raise MicrositeSchemaError(
            f"{prefix}Block {index} ({block_type}): 'props' must be an object."
        )

    schema = BLOCK_SCHEMA[block_type]
    required = schema["required"]
    optional = schema["optional"]
    nested = schema["nested"]
    validators: dict[str, Callable] = schema.get("validators", {})

    # Check required props
    for key in required:
        value = props.get(key)
        if value in (None, "", [], {}):
            raise MicrositeSchemaError(
                f"{prefix}Block {index} ({block_type}): required prop '{key}' is missing or empty."
            )

    # Build set of all allowed prop names (scalar + nested)
    all_allowed = set(required + optional + nested)
    unknown = set(props.keys()) - all_allowed
    if unknown:
        raise MicrositeSchemaError(
            f"{prefix}Block {index} ({block_type}): unknown props: {', '.join(sorted(unknown))}."
        )

    # Run per-prop validators for scalar props
    for prop_name, validator in validators.items():
        value = props.get(prop_name)
        if value is not None:
            validator(value, prop_name)

    # Recurse into nested block lists
    normalised_nested: dict[str, list] = {}
    for nested_key in nested:
        sub_list = props.get(nested_key, [])
        if not isinstance(sub_list, list):
            raise MicrositeSchemaError(
                f"{prefix}Block {index} ({block_type}): '{nested_key}' must be a list."
            )
        normalised_nested[nested_key] = [
            _validate_block(sub, sub_i, prefix=f"{prefix}Block {index}.{nested_key}.")
            for sub_i, sub in enumerate(sub_list)
        ]

    # Build normalised props (scalar props only)
    normalised_props = {
        k: v for k, v in props.items() if k not in nested
    }
    normalised_props.update(normalised_nested)

    return {"type": block_type, "props": normalised_props}


def validate_builder_payload(payload: Any) -> dict[str, Any]:
    """
    Validate and normalise a builder payload dict.

    Raises MicrositeSchemaError on any validation failure.
    Returns a normalised payload dict on success.
    """
    if not isinstance(payload, dict):
        raise MicrositeSchemaError("Payload must be a JSON object.")

    blocks_raw = payload.get("blocks")
    if not isinstance(blocks_raw, list):
        raise MicrositeSchemaError("'blocks' must be a list.")

    normalised_blocks = [
        _validate_block(block, i) for i, block in enumerate(blocks_raw)
    ]

    return {
        "version": int(payload.get("version", 1)),
        "blocks": normalised_blocks,
    }
