from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Project, Experience


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    
    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "tech_stack",
            "github_url",
            "year",
            "project_url",
            "project_image_url",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = ["id"]


    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer untuk membaca dan mengelola Experience."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )

    is_ongoing = serializers.ReadOnlyField()

    class Meta:
        model = Experience
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_display",
            "thumbnail",
            "started_at",
            "ended_at",
            "is_ongoing",
            "star_count",
            "is_starred",
        ]
        read_only_fields = ["id", "started_at"]

    def validate_title(self, value):
        """Bersihkan HTML dan tolak judul kosong."""
        value = strip_tags(value).strip()

        if not value:
            raise serializers.ValidationError(
                "Nama pengalaman tidak boleh kosong."
            )

        return value

    def validate_description(self, value):
        """Bersihkan HTML dan tolak deskripsi kosong."""
        value = strip_tags(value).strip()

        if not value:
            raise serializers.ValidationError(
                "Deskripsi tidak boleh kosong."
            )

        return value

    def get_star_count(self, obj):
        """Hitung jumlah pengguna yang memberi star."""
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        """Periksa status star pengguna yang sedang login."""
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return False

        return any(
            user.pk == request.user.pk
            for user in obj.starred_by.all()
        )
