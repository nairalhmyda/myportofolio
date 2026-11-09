from django.shortcuts import get_object_or_404
from django.db.models.functions import Lower
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Experience, Project
from main.permissions import (
    IsPortfolioOwnerOrReadOnly,
    IsPortfolioOwnerOrEditorOrReadOnly,
)
from main.serializers import ProjectSerializer, ExperienceSerializer


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("starred_by").order_by("title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related("starred_by"), pk=project_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    """Menampilkan, mencari, atau menambahkan Experience."""

    
    if request.method == "GET":
        experiences = Experience.objects.prefetch_related(
            "starred_by"
        )

        title = request.query_params.get("title", "").strip()
        category = request.query_params.get("category", "").strip()
        ordering = request.query_params.get("ordering", "newest").strip()

        if title:
            experiences = experiences.filter(
                title__icontains=title
            )

        valid_categories = {
            value for value, label in Experience.EXPERIENCE_CHOICES
        }

        if category:
            if category not in valid_categories:
                return Response(
                    {"category": ["Kategori tidak valid."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            experiences = experiences.filter(category=category)

        sort_options = {
            "newest": ("-started_at", "-id"),
            "oldest": ("started_at", "id"),
            "title_asc": (Lower("title"), "id"),
        }

        if ordering not in sort_options:
            return Response(
                {"ordering": ["Pilihan urutan tidak valid."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        experiences = experiences.order_by(*sort_options[ordering])

        serializer = ExperienceSerializer(
            experiences,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


    serializer = ExperienceSerializer(
        data=request.data,
        context={"request": request},
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    """Mengambil, mengubah, atau menghapus satu Experience."""

    experience = get_object_or_404(
        Experience.objects.prefetch_related("starred_by"),
        pk=experience_id,
    )

    if request.method == "GET":
        serializer = ExperienceSerializer(
            experience,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    if request.method == "DELETE":
        experience.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    serializer = ExperienceSerializer(
        experience,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    """Menambah atau membatalkan star milik pengguna login."""

    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )

    if experience.starred_by.filter(
        pk=request.user.pk
    ).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)

    serializer = ExperienceSerializer(
        experience,
        context={"request": request},
    )

    return Response(
        serializer.data,
        status=status.HTTP_200_OK,
    )
