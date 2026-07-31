"""
Tests for the Wagtail Microsite Builder schema validation layer.
"""

from django.test import TestCase

from wagtail_microsites.schema import (
    BLOCK_SCHEMA,
    MicrositeSchemaError,
    validate_builder_payload,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _payload(*blocks):
    """Wrap a list of block dicts into a minimal valid payload."""
    return {"version": 1, "blocks": list(blocks)}


def _block(block_type, **props):
    return {"type": block_type, "props": props}


# ---------------------------------------------------------------------------
# Top-level payload validation
# ---------------------------------------------------------------------------


class PayloadStructureTests(TestCase):
    def test_valid_empty_payload(self):
        result = validate_builder_payload({"blocks": []})
        self.assertEqual(result["blocks"], [])
        self.assertEqual(result["version"], 1)

    def test_payload_must_be_dict(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload([])

    def test_blocks_must_be_list(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload({"blocks": "not-a-list"})

    def test_unknown_block_type_rejected(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("marquee", text="hi")))

    def test_version_defaults_to_one(self):
        result = validate_builder_payload({"blocks": []})
        self.assertEqual(result["version"], 1)

    def test_version_preserved(self):
        result = validate_builder_payload({"version": 2, "blocks": []})
        self.assertEqual(result["version"], 2)


# ---------------------------------------------------------------------------
# Hero block
# ---------------------------------------------------------------------------


class HeroBlockTests(TestCase):
    def _valid(self, **extra_props):
        return _payload(_block("hero", headline="Save the Wetlands", **extra_props))

    def test_valid_minimal(self):
        result = validate_builder_payload(self._valid())
        self.assertEqual(result["blocks"][0]["type"], "hero")

    def test_missing_required_headline(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("hero")))

    def test_unknown_prop_rejected(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(arbitrary_css="color:red"))

    def test_valid_full_overlay_props(self):
        result = validate_builder_payload(
            self._valid(
                overlay_heading_level="h2",
                overlay_font_weight="extrabold",
                overlay_font_size="3rem",
                overlay_font_family="Georgia, serif",
                overlay_text_color="#ffffff",
                overlay_horizontal_align="left",
                overlay_vertical_align="bottom",
            )
        )
        props = result["blocks"][0]["props"]
        self.assertEqual(props["overlay_heading_level"], "h2")
        self.assertEqual(props["overlay_font_weight"], "extrabold")

    def test_invalid_heading_level(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(overlay_heading_level="h7"))

    def test_invalid_font_weight(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(overlay_font_weight="ultra"))

    def test_invalid_font_size(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(overlay_font_size="big"))

    def test_invalid_horizontal_align(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(overlay_horizontal_align="justify"))

    def test_invalid_vertical_align(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(overlay_vertical_align="middle"))

    def test_unsafe_background_url_rejected(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                self._valid(background_image_url="javascript:alert(1)")
            )

    def test_safe_background_url_accepted(self):
        result = validate_builder_payload(
            self._valid(background_image_url="https://example.com/img.jpg")
        )
        self.assertIn("background_image_url", result["blocks"][0]["props"])


# ---------------------------------------------------------------------------
# CTA Band block
# ---------------------------------------------------------------------------


class CTABandBlockTests(TestCase):
    def _valid(self, **extra):
        return _payload(
            _block(
                "cta_band",
                headline="Join us",
                cta_text="Get involved",
                cta_url="https://example.com",
                **extra,
            )
        )

    def test_valid(self):
        result = validate_builder_payload(self._valid())
        self.assertEqual(result["blocks"][0]["type"], "cta_band")

    def test_missing_headline(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("cta_band", cta_text="Go", cta_url="https://example.com"))
            )

    def test_missing_cta_url(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("cta_band", headline="Hi", cta_text="Go"))
            )

    def test_unsafe_cta_url(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(
                    _block(
                        "cta_band",
                        headline="Hi",
                        cta_text="Go",
                        cta_url="javascript:void(0)",
                    )
                )
            )


# ---------------------------------------------------------------------------
# Quote block
# ---------------------------------------------------------------------------


class QuoteBlockTests(TestCase):
    def test_valid_minimal(self):
        result = validate_builder_payload(_payload(_block("quote", text="Great words.")))
        self.assertEqual(result["blocks"][0]["props"]["text"], "Great words.")

    def test_missing_text(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("quote")))

    def test_invalid_source_url(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("quote", text="...", source_url="ftp://bad.com"))
            )

    def test_valid_https_source_url(self):
        result = validate_builder_payload(
            _payload(
                _block("quote", text="...", source_url="https://example.com/article")
            )
        )
        self.assertIn("source_url", result["blocks"][0]["props"])


# ---------------------------------------------------------------------------
# Two-column block
# ---------------------------------------------------------------------------


class TwoColumnBlockTests(TestCase):
    def _valid(self, **extra):
        return _payload(_block("two_column", **extra))

    def test_valid_empty_columns(self):
        result = validate_builder_payload(self._valid())
        self.assertEqual(result["blocks"][0]["type"], "two_column")

    def test_valid_ratio(self):
        result = validate_builder_payload(self._valid(ratio="40/60"))
        self.assertEqual(result["blocks"][0]["props"]["ratio"], "40/60")

    def test_invalid_ratio(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(ratio="wide"))

    def test_ratio_out_of_range(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(ratio="0/100"))

    def test_invalid_stack_on_mobile(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(self._valid(stack_on_mobile="yes"))

    def test_nested_left_blocks_validated(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                self._valid(
                    left_blocks=[_block("marquee", text="no")]
                )
            )

    def test_nested_valid_sub_blocks(self):
        result = validate_builder_payload(
            self._valid(
                ratio="67/33",
                left_blocks=[_block("quote", text="Something important.")],
                right_blocks=[_block("card", title="A card")],
            )
        )
        cols = result["blocks"][0]["props"]
        self.assertEqual(len(cols["left_blocks"]), 1)
        self.assertEqual(cols["left_blocks"][0]["type"], "quote")


# ---------------------------------------------------------------------------
# Three-column block
# ---------------------------------------------------------------------------


class ThreeColumnBlockTests(TestCase):
    def test_valid_empty(self):
        result = validate_builder_payload(_payload(_block("three_column")))
        self.assertEqual(result["blocks"][0]["type"], "three_column")

    def test_nested_blocks_validated(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("three_column", col1_blocks=[_block("bad_type")]))
            )


# ---------------------------------------------------------------------------
# Card block
# ---------------------------------------------------------------------------


class CardBlockTests(TestCase):
    def test_valid_minimal(self):
        result = validate_builder_payload(_payload(_block("card", title="My card")))
        self.assertEqual(result["blocks"][0]["props"]["title"], "My card")

    def test_missing_title(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("card")))

    def test_invalid_image_url(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("card", title="X", image_url="data:image/png;base64,abc"))
            )


# ---------------------------------------------------------------------------
# Rich text block
# ---------------------------------------------------------------------------


class RichTextBlockTests(TestCase):
    def test_valid(self):
        result = validate_builder_payload(
            _payload(_block("rich_text", body="<p>Hello</p>"))
        )
        self.assertEqual(result["blocks"][0]["props"]["body"], "<p>Hello</p>")

    def test_missing_body(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("rich_text")))


# ---------------------------------------------------------------------------
# Donation embed block
# ---------------------------------------------------------------------------


class DonationEmbedBlockTests(TestCase):
    def test_valid_donation(self):
        result = validate_builder_payload(
            _payload(_block("donation_embed", embed_type="donation"))
        )
        self.assertEqual(result["blocks"][0]["props"]["embed_type"], "donation")

    def test_valid_signup(self):
        result = validate_builder_payload(
            _payload(_block("donation_embed", embed_type="signup"))
        )
        self.assertEqual(result["blocks"][0]["props"]["embed_type"], "signup")

    def test_invalid_embed_type(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("donation_embed", embed_type="paypal"))
            )

    def test_missing_embed_type(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("donation_embed")))

    def test_invalid_embed_url(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(
                    _block(
                        "donation_embed",
                        embed_type="donation",
                        embed_url="javascript:alert(1)",
                    )
                )
            )

    def test_valid_https_embed_url(self):
        result = validate_builder_payload(
            _payload(
                _block(
                    "donation_embed",
                    embed_type="donation",
                    embed_url="https://donate.example.org/form",
                )
            )
        )
        self.assertIn("embed_url", result["blocks"][0]["props"])


# ---------------------------------------------------------------------------
# Alert banner block
# ---------------------------------------------------------------------------


class AlertBannerBlockTests(TestCase):
    def test_valid_minimal(self):
        result = validate_builder_payload(
            _payload(_block("alert_banner", message="Site maintenance tonight."))
        )
        self.assertEqual(result["blocks"][0]["type"], "alert_banner")

    def test_invalid_level(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("alert_banner", message="X", level="critical"))
            )

    def test_valid_levels(self):
        for level in ("info", "warning", "success", "error"):
            result = validate_builder_payload(
                _payload(_block("alert_banner", message="X", level=level))
            )
            self.assertEqual(result["blocks"][0]["props"]["level"], level)

    def test_dismissible_must_be_bool(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("alert_banner", message="X", dismissible="true"))
            )

    def test_missing_message(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("alert_banner")))


# ---------------------------------------------------------------------------
# FAQ block
# ---------------------------------------------------------------------------


class FAQBlockTests(TestCase):
    def _valid_items(self):
        return [{"question": "What?", "answer": "This."}]

    def test_valid(self):
        result = validate_builder_payload(
            _payload(_block("faq", items=self._valid_items()))
        )
        self.assertEqual(result["blocks"][0]["type"], "faq")

    def test_missing_items(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("faq")))

    def test_empty_items_list(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(_payload(_block("faq", items=[])))

    def test_item_missing_question(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("faq", items=[{"answer": "Because."}]))
            )

    def test_item_missing_answer(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(_block("faq", items=[{"question": "Why?"}]))
            )

    def test_item_unknown_key(self):
        with self.assertRaises(MicrositeSchemaError):
            validate_builder_payload(
                _payload(
                    _block(
                        "faq",
                        items=[{"question": "Why?", "answer": "Because.", "extra": "nope"}],
                    )
                )
            )

    def test_multiple_items(self):
        items = [
            {"question": f"Q{i}", "answer": f"A{i}"} for i in range(5)
        ]
        result = validate_builder_payload(_payload(_block("faq", items=items)))
        self.assertEqual(len(result["blocks"][0]["props"]["items"]), 5)


# ---------------------------------------------------------------------------
# All approved block types are present in BLOCK_SCHEMA
# ---------------------------------------------------------------------------


class BlockSchemaRegistryTests(TestCase):
    EXPECTED_BLOCK_TYPES = {
        "hero",
        "cta_band",
        "quote",
        "two_column",
        "three_column",
        "card",
        "rich_text",
        "donation_embed",
        "alert_banner",
        "faq",
    }

    def test_all_expected_block_types_registered(self):
        self.assertEqual(set(BLOCK_SCHEMA.keys()), self.EXPECTED_BLOCK_TYPES)
