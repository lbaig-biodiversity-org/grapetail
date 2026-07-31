"""
Tests for the MicrositePage model — rendering and validation behaviour.
"""

from django.test import TestCase, RequestFactory
from wagtail.models import Page, Site

from wagtail_microsites.models import MicrositePage
from wagtail_microsites.schema import MicrositeSchemaError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_page(**kwargs) -> MicrositePage:
    """Build (but do not save) a MicrositePage with sane defaults."""
    return MicrositePage(
        title=kwargs.get("title", "Test Microsite"),
        slug=kwargs.get("slug", "test-microsite"),
        theme=kwargs.get("theme", "default"),
        builder_json=kwargs.get("builder_json", {"blocks": []}),
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


class MicrositePageRenderingTests(TestCase):
    def test_render_empty_payload(self):
        page = _make_page(builder_json={"blocks": []})
        output = page.render_builder()
        self.assertEqual(output, "")

    def test_render_hero_block(self):
        page = _make_page(
            builder_json={
                "version": 1,
                "blocks": [
                    {
                        "type": "hero",
                        "props": {
                            "headline": "Save the Wetlands",
                            "subheadline": "Act now",
                            "cta_text": "Donate",
                            "cta_url": "https://example.com/donate",
                        },
                    }
                ],
            }
        )
        html = page.render_builder()
        self.assertIn("Save the Wetlands", html)
        self.assertIn("Act now", html)
        self.assertIn("Donate", html)
        self.assertIn("https://example.com/donate", html)
        self.assertIn("ms-hero", html)

    def test_render_quote_block(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "quote",
                        "props": {
                            "text": "We cannot wait.",
                            "attribution": "Campaign Lead",
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("We cannot wait.", html)
        self.assertIn("Campaign Lead", html)
        self.assertIn("ms-quote", html)

    def test_render_cta_band(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "cta_band",
                        "props": {
                            "headline": "Join us",
                            "cta_text": "Sign up",
                            "cta_url": "https://example.com/signup",
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("Join us", html)
        self.assertIn("Sign up", html)
        self.assertIn("ms-cta-band", html)

    def test_render_alert_banner(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "alert_banner",
                        "props": {
                            "message": "Important update",
                            "level": "warning",
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("Important update", html)
        self.assertIn("ms-alert-banner--warning", html)

    def test_render_faq_block(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "faq",
                        "props": {
                            "headline": "Common questions",
                            "items": [
                                {"question": "Why?", "answer": "Because."},
                                {"question": "How?", "answer": "Like this."},
                            ],
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("Common questions", html)
        self.assertIn("Why?", html)
        self.assertIn("Because.", html)

    def test_render_card_block(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "card",
                        "props": {
                            "title": "My Card",
                            "body": "Card description.",
                            "cta_text": "Read more",
                            "cta_url": "https://example.com",
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("My Card", html)
        self.assertIn("Card description.", html)
        self.assertIn("ms-card", html)

    def test_render_rich_text_block(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "rich_text",
                        "props": {"body": "<p>Hello <strong>world</strong>.</p>"},
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("<strong>world</strong>", html)
        self.assertIn("ms-rich-text", html)

    def test_render_two_column_with_sub_blocks(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "two_column",
                        "props": {
                            "ratio": "40/60",
                            "left_blocks": [
                                {"type": "quote", "props": {"text": "Left side."}}
                            ],
                            "right_blocks": [
                                {"type": "card", "props": {"title": "Right card"}}
                            ],
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("ms-two-column", html)
        self.assertIn("Left side.", html)
        self.assertIn("Right card", html)
        self.assertIn("40fr", html)
        self.assertIn("60fr", html)

    def test_render_three_column(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "three_column",
                        "props": {
                            "col1_blocks": [{"type": "card", "props": {"title": "C1"}}],
                            "col2_blocks": [{"type": "card", "props": {"title": "C2"}}],
                            "col3_blocks": [{"type": "card", "props": {"title": "C3"}}],
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("ms-three-column", html)
        self.assertIn("C1", html)
        self.assertIn("C2", html)
        self.assertIn("C3", html)

    def test_render_donation_embed_with_url(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "donation_embed",
                        "props": {
                            "embed_type": "donation",
                            "embed_url": "https://donate.example.org/form",
                            "title": "Donate Now",
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("ms-donation-embed", html)
        self.assertIn("Donate Now", html)
        self.assertIn("https://donate.example.org/form", html)
        self.assertIn("<iframe", html)

    def test_render_donation_embed_with_form_id(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "donation_embed",
                        "props": {
                            "embed_type": "signup",
                            "form_id": "abc123",
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertIn("abc123", html)
        self.assertNotIn("<iframe", html)

    def test_multiple_blocks_in_order(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {"type": "hero", "props": {"headline": "Block 1"}},
                    {"type": "quote", "props": {"text": "Block 2"}},
                    {"type": "alert_banner", "props": {"message": "Block 3"}},
                ]
            }
        )
        html = page.render_builder()
        pos1 = html.index("Block 1")
        pos2 = html.index("Block 2")
        pos3 = html.index("Block 3")
        self.assertLess(pos1, pos2)
        self.assertLess(pos2, pos3)


# ---------------------------------------------------------------------------
# Hero overlay styling in rendered HTML
# ---------------------------------------------------------------------------


class HeroOverlayRenderingTests(TestCase):
    def _render(self, **extra_props):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "hero",
                        "props": {"headline": "Test", **extra_props},
                    }
                ]
            }
        )
        return page.render_builder()

    def test_default_heading_level_is_h1(self):
        html = self._render()
        self.assertIn("<h1", html)

    def test_custom_heading_level(self):
        html = self._render(overlay_heading_level="h2")
        self.assertIn("<h2", html)
        self.assertNotIn("<h1", html)

    def test_font_size_in_style(self):
        html = self._render(overlay_font_size="3rem")
        self.assertIn("3rem", html)

    def test_text_color_in_style(self):
        html = self._render(overlay_text_color="#ff0000")
        self.assertIn("#ff0000", html)

    def test_font_weight_class(self):
        html = self._render(overlay_font_weight="extrabold")
        self.assertIn("weight-extrabold", html)

    def test_horizontal_align_class(self):
        html = self._render(overlay_horizontal_align="left")
        self.assertIn("ms-hero--h-left", html)

    def test_vertical_align_class(self):
        html = self._render(overlay_vertical_align="bottom")
        self.assertIn("ms-hero--v-bottom", html)


# ---------------------------------------------------------------------------
# Security: XSS / unsafe URL sanitisation in rendered output
# ---------------------------------------------------------------------------


class RenderingSecurityTests(TestCase):
    def test_hero_headline_escaped(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "hero",
                        "props": {"headline": '<script>alert("xss")</script>'},
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_unsafe_cta_url_not_rendered(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "hero",
                        "props": {
                            "headline": "Safe",
                            "cta_text": "Click",
                            "cta_url": "javascript:alert(1)",
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertNotIn("javascript:", html)

    def test_rich_text_script_stripped(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "rich_text",
                        "props": {
                            "body": '<p>Safe</p><script>evil()</script>'
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertNotIn("<script>", html)
        self.assertIn("Safe", html)

    def test_rich_text_event_handler_stripped(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "rich_text",
                        "props": {
                            "body": '<p onclick="evil()">Click</p>'
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertNotIn("onclick", html)
        self.assertIn("Click", html)

    def test_card_image_unsafe_url_not_rendered(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "card",
                        "props": {
                            "title": "My card",
                            "image_url": "data:image/svg+xml,<svg onload=alert(1)>",
                        },
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertNotIn("data:image", html)

    def test_alert_banner_message_escaped(self):
        page = _make_page(
            builder_json={
                "blocks": [
                    {
                        "type": "alert_banner",
                        "props": {"message": '<b onclick="x()">Bold</b>'},
                    }
                ]
            }
        )
        html = page.render_builder()
        self.assertNotIn("<b", html)


# ---------------------------------------------------------------------------
# rendered_preview cache
# ---------------------------------------------------------------------------


class RenderedPreviewTests(TestCase):
    def test_render_builder_output_is_string(self):
        page = _make_page(
            builder_json={
                "blocks": [{"type": "quote", "props": {"text": "Hello"}}]
            }
        )
        result = page.render_builder()
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
