from django import forms


class MicrositeBuilderWidget(forms.Textarea):
    template_name = "wagtail_microsites/widgets/microsite_builder.html"
