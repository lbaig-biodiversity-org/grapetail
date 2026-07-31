"""
MicrositePage — a Wagtail Page that stores its content as a validated JSON
schema, rendered server-side via Django templates.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page

from .schema import MicrositeSchemaError, validate_builder_payload


class MicrositePage(Page):
    """
    A short-lived campaign/microsite page whose layout is defined by a
    constrained JSON builder schema rather than the usual Wagtail StreamField.

    Content flow
    ------------
    1. Editor uses the GrapesJS-based builder panel (or raw JSON in dev) to
       compose a page from approved block types.
    2. On save, ``clean()`` validates the JSON against BLOCK_SCHEMA.
    3. ``render_builder()`` turns the validated JSON into HTML by calling
       individual block templates — the server, not the browser, controls
       rendering.
    4. The resulting HTML is cached in ``rendered_preview`` so the public
       page serve is fast (no template re-execution on every request).
    """

    # -----------------------------------------------------------------------
    # Fields
    # -----------------------------------------------------------------------

    theme = models.CharField(
        max_length=50,
        default="default",
        help_text=(
            "Choose a brand theme variant for this microsite. "
            "Controls colour palette and typography applied via CSS."
        ),
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Optional expiry date/time. After this the page can be "
            "automatically unpublished or archived by a scheduled task."
        ),
    )

    # The canonical content representation — a validated JSON schema.
    builder_json = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Constrained block schema produced by the visual builder. "
            "Only approved block types and props are accepted."
        ),
    )

    # Pre-rendered HTML cache — regenerated on every save.
    rendered_preview = models.TextField(blank=True, editable=False)

    # -----------------------------------------------------------------------
    # Wagtail admin panels
    # -----------------------------------------------------------------------

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("theme"),
                FieldPanel("expires_at"),
            ],
            heading="Microsite settings",
        ),
        # The builder_json field is presented as-is here (raw JSON textarea)
        # and replaced by the GrapesJS widget in production via the custom
        # MicrositeBuilderPanel defined in panels.py.
        FieldPanel("builder_json", classname="microsite-builder-panel"),
    ]

    # -----------------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------------

    def clean(self) -> None:
        super().clean()
        try:
            self.builder_json = validate_builder_payload(
                self.builder_json or {"blocks": []}
            )
        except MicrositeSchemaError as exc:
            raise ValidationError({"builder_json": str(exc)}) from exc

    # -----------------------------------------------------------------------
    # Save / rendering
    # -----------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:  # type: ignore[override]
        # Ensure validation runs even on direct model saves.
        try:
            self.full_clean()
        except ValidationError:
            # Re-raise so callers get useful feedback.
            raise
        self.rendered_preview = self.render_builder()
        super().save(*args, **kwargs)

    def render_builder(self) -> str:
        """Render each block in builder_json through its template."""
        blocks = (self.builder_json or {}).get("blocks", [])
        parts: list[str] = []
        for block in blocks:
            parts.append(self._render_block(block))
        return "\n".join(parts)

    @staticmethod
    def _render_block(block: dict) -> str:
        """Render a single block dict using its template."""
        block_type = block.get("type", "")
        template = f"wagtail_microsites/blocks/{block_type}.html"
        return render_to_string(template, {"block": block, "props": block.get("props", {})})

    # -----------------------------------------------------------------------
    # Request context
    # -----------------------------------------------------------------------

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["rendered_builder"] = (
            self.rendered_preview or self.render_builder()
        )
        context["is_expired"] = (
            self.expires_at is not None and timezone.now() > self.expires_at
        )
        return context

    # -----------------------------------------------------------------------
    # Meta
    # -----------------------------------------------------------------------

    template = "wagtail_microsites/pages/microsite_page.html"

    class Meta:
        verbose_name = "Microsite page"
        verbose_name_plural = "Microsite pages"
