"""Tests for microsite admin/editor integration."""

from django.test import SimpleTestCase

from wagtail_microsites.models import MicrositePage
from wagtail_microsites.widgets import MicrositeBuilderWidget


class MicrositeBuilderPanelTests(SimpleTestCase):
    def test_builder_panel_uses_custom_widget(self):
        panel = next(
            p
            for p in MicrositePage.content_panels
            if getattr(p, "field_name", "") == "builder_json"
        )
        self.assertIs(panel.widget, MicrositeBuilderWidget)


class MicrositeBuilderWidgetTests(SimpleTestCase):
    def test_widget_renders_visual_builder_shell(self):
        widget = MicrositeBuilderWidget()
        html = widget.render(
            "builder_json",
            '{"version": 1, "blocks": []}',
            attrs={"id": "id_builder_json"},
        )
        self.assertIn('data-builder-widget', html)
        self.assertIn('data-builder-canvas', html)
        self.assertIn('name="builder_json"', html)
        self.assertIn('Advanced: raw JSON', html)
