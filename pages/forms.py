from django import forms

from .models import Resource


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            "title",
            "description",
            "resource_type",
            "category",
            "available",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Python Basics"}),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Brief description of the resource..."}
            ),
            "resource_type": forms.TextInput(attrs={"placeholder": "e.g. Article, Book, Course"}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        normalized_title = title.strip()
        if len(normalized_title) < 3:
            raise forms.ValidationError("The title must contain at least 3 characters.")
        return normalized_title
