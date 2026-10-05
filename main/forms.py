from django.core.exceptions import ValidationError
from django.forms import ModelForm, NumberInput, Textarea, TextInput, URLInput
from django.utils.html import strip_tags

from main.models import Experience, Project


class SanitizedTextMixin:
    """Strip HTML tags from plain-text fields before saving them."""

    sanitized_fields = ()

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.sanitized_fields:
            value = cleaned_data.get(field_name)
            if isinstance(value, str):
                cleaned_data[field_name] = strip_tags(value).strip()
        return cleaned_data


class ProjectForm(SanitizedTextMixin, ModelForm):
    sanitized_fields = ("title", "description", "tech_stack")

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "github_url",
            "year",
            "project_image_url",
        ]
        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "github_url": "URL GitHub",
            "year": "Tahun",
            "project_image_url": "URL Gambar Proyek",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Contoh: Web Portfolio",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan tentang proyek ini",
                    "rows": 4,
                }
            ),
            "tech_stack": TextInput(
                attrs={"placeholder": "Django, Python, HTML, CSS"}
            ),
            "github_url": URLInput(
                attrs={"placeholder": "https://github.com/username/project"}
            ),
            "year": NumberInput(attrs={"placeholder": "2026"}),
            "project_image_url": URLInput(
                attrs={"placeholder": "https://example.com/project-image.jpg"}
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh kosong.")
        return title


class ExperienceForm(SanitizedTextMixin, ModelForm):
    sanitized_fields = ("title", "description")

    class Meta:
        model = Experience
        fields = ["title", "description", "category", "thumbnail", "ended_at"]
        labels = {
            "title": "Nama Pengalaman",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "Thumbnail URL",
            "ended_at": "Tanggal Selesai",
        }
        widgets = {
            "title": TextInput(
                attrs={"placeholder": "Contoh: Staff BEM Fasilkom UI"}
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan pengalaman ini",
                    "rows": 5,
                }
            ),
            "thumbnail": URLInput(
                attrs={"placeholder": "https://example.com/image.jpg"}
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama pengalaman tidak boleh kosong.")
        return title
