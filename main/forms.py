from django.forms import (
    ModelForm,
    TextInput,
    Textarea,
    URLInput,
    NumberInput,
)

from main.models import Project, Experience
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags


class ProjectForm(ModelForm):
    class Meta:
        model = Project

        fields = [
            "title",
            "description",
            "tech_stack",
            "github_url",
            "year",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "github_url": "URL GitHub",
            "year": "Tahun",
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
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "github_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/username/project",
                }
            ),
            "year": NumberInput(
                attrs={
                    "placeholder": "2026",
                }
            ),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

class ExperienceForm(ModelForm):
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
            "title": TextInput(attrs={
                "placeholder": "Contoh: Staff BEM Fasilkom UI",
            }),
            "description": Textarea(attrs={
                "placeholder": "Jelaskan pengalaman ini",
                "rows": 5,
            }),
            "thumbnail": URLInput(attrs={
                "placeholder": "https://example.com/image.jpg",
            }),
        }
