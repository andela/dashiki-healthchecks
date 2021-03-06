from django import forms
from hc.api.models import Channel
from hc.front.models import Post
from hc.front.models import FaqItem, FaqCategory
from ckeditor.widgets import CKEditorWidget


class NameTagsForm(forms.Form):
    name = forms.CharField(max_length=100, required=False)
    tags = forms.CharField(max_length=500, required=False)

    def clean_tags(self):
        l = []

        for part in self.cleaned_data["tags"].split(" "):
            part = part.strip()
            if part != "":
                l.append(part)

        return " ".join(l)


class TimeoutForm(forms.Form):
    timeout = forms.IntegerField(min_value=60, max_value=2592000)
    grace = forms.IntegerField(min_value=60, max_value=2592000)


class NagTimeForm(forms.Form):
    nag_time = forms.IntegerField(min_value=60, max_value=2592000)


class AddChannelForm(forms.ModelForm):

    class Meta:
        model = Channel
        fields = ['kind', 'value']

    def clean_value(self):
        value = self.cleaned_data["value"]
        return value.strip()


class AddWebhookForm(forms.Form):
    error_css_class = "has-error"

    value_down = forms.URLField(max_length=1000, required=False)
    value_up = forms.URLField(max_length=1000, required=False)

    def get_value(self):
        return "{value_down}\n{value_up}".format(**self.cleaned_data)


class PostForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Title",
                "style": 'width: 98%'
            }),
        strip=True,
        label=""
    )
    body = forms.CharField(widget=CKEditorWidget(), label="")

    class Meta:
        model = Post
        fields = ("title", "body",)


class AddFaqForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorWidget(), label="")

    class Meta:
        model = FaqItem
        fields = ['category', 'title', 'body']


class AddFaqCategoryForm(forms.ModelForm):

    class Meta:
        model = FaqCategory
        fields = ['category']
