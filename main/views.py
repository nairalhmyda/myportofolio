from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project


PORTFOLIO_OWNER = "Naira Al Humayda"


def is_editor(user):
    """Return True when an authenticated user belongs to the Editor group."""
    return user.is_authenticated and user.groups.filter(name="Editor").exists()


def wants_json(request):
    """Detect fetch/AJAX requests that expect a JSON response."""
    accept = request.headers.get("Accept", "")
    return (
        "application/json" in accept
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )


def show_main(request):
    context = {
        "name": PORTFOLIO_OWNER,
        "npm": "2506532233",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada Data Science."
        ),
        "last_login": request.COOKIES.get(
            "last_login",
            "Belum ada sesi login / Cookie tidak ditemukan",
        ),
    }
    return render(request, "index.html", context)


def show_projects(request):
    context = {
        "name": PORTFOLIO_OWNER,
        "title_query": request.GET.get("title", "").strip(),
        "form": ProjectForm(),
        "is_editor": is_editor(request.user),
    }
    return render(request, "projects.html", context)


def show_experience(request):
    context = {
        "name": PORTFOLIO_OWNER,
        "title_query": request.GET.get("title", "").strip(),
        "form": ExperienceForm(),
        "is_editor": is_editor(request.user),
    }
    return render(request, "experience.html", context)


# Project CRUD + JSON/AJAX endpoints


def get_projects_json(request):
    """Return public project data plus per-user star state for dynamic rendering."""
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related("starred_by")

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        user_is_starred = (
            request.user.is_authenticated
            and any(user.pk == request.user.pk for user in starred_users)
        )

        data.append(
            {
                "id": project.pk,
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "github_url": project.github_url or "",
                "project_image_url": project.project_image_url or "",
                "year": project.year,
                "star_count": len(starred_users),
                "is_starred": user_is_starred,
                "starred_by_names": [user.username for user in starred_users],
                "urls": {
                    "edit": reverse("main:update_project", args=[project.pk]),
                    "delete": reverse("main:delete_project", args=[project.pk]),
                    "star": reverse("main:toggle_star", args=[project.pk]),
                },
            }
        )

    return JsonResponse(
        {
            "items": data,
            "permissions": {
                "can_edit": request.user.is_superuser or is_editor(request.user),
                "can_delete": request.user.is_superuser,
                "can_star": request.user.is_authenticated,
            },
        }
    )


@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    return render(
        request,
        "projects_form.html",
        {
            "name": PORTFOLIO_OWNER,
            "form": form,
            "page_title": "Tambah Project",
            "submit_label": "Tambah Project",
        },
    )


@login_required(login_url="/login/")
def update_project(request, project_id):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")

    return render(
        request,
        "projects_form.html",
        {
            "name": PORTFOLIO_OWNER,
            "form": form,
            "page_title": "Edit Project",
            "submit_label": "Simpan Perubahan",
            "project": project,
        },
    )


@login_required(login_url="/login/")
@require_POST
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    project.delete()

    if wants_json(request):
        return JsonResponse({"message": "Proyek berhasil dihapus."})

    messages.success(request, "Proyek berhasil dihapus!")
    return redirect("main:show_projects")


@login_required(login_url="/login/")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
        is_starred = False
    else:
        project.starred_by.add(request.user)
        is_starred = True

    if wants_json(request):
        return JsonResponse(
            {
                "is_starred": is_starred,
                "star_count": project.starred_by.count(),
            }
        )

    return redirect("main:show_projects")


@login_required(login_url="/login/")
@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    project = form.save()
    return JsonResponse(
        {
            "message": "Proyek berhasil ditambahkan.",
            "id": project.pk,
        },
        status=201,
    )


# Experience CRUD + JSON/AJAX endpoints


def get_experiences_json(request):
    """Return Experience data in a frontend-friendly JSON contract."""
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.prefetch_related("starred_by")

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    data = []
    for experience in experiences:
        starred_users = list(experience.starred_by.all())
        user_is_starred = (
            request.user.is_authenticated
            and any(user.pk == request.user.pk for user in starred_users)
        )

        data.append(
            {
                "id": str(experience.pk),
                "title": experience.title,
                "description": experience.description,
                "category": experience.category,
                "category_display": experience.get_category_display(),
                "thumbnail": experience.thumbnail or "",
                "is_ongoing": experience.is_ongoing,
                "started_at": experience.started_at.isoformat(),
                "ended_at": (
                    experience.ended_at.isoformat() if experience.ended_at else None
                ),
                "star_count": len(starred_users),
                "is_starred": user_is_starred,
                "starred_by_names": [user.username for user in starred_users],
                "urls": {
                    "edit": reverse("main:update_experience", args=[experience.pk]),
                    "delete": reverse("main:delete_experience", args=[experience.pk]),
                    "star": reverse("main:toggle_experience_star", args=[experience.pk]),
                },
            }
        )

    return JsonResponse(
        {
            "items": data,
            "permissions": {
                "can_edit": request.user.is_superuser or is_editor(request.user),
                "can_delete": request.user.is_superuser,
                "can_star": request.user.is_authenticated,
            },
        }
    )


@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    return render(
        request,
        "experience_form.html",
        {
            "name": PORTFOLIO_OWNER,
            "form": form,
            "page_title": "Tambah Pengalaman",
            "submit_label": "Tambah Pengalaman",
        },
    )


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_experience")

    return render(
        request,
        "experience_form.html",
        {
            "name": PORTFOLIO_OWNER,
            "form": form,
            "page_title": "Edit Pengalaman",
            "submit_label": "Simpan Perubahan",
            "experience": experience,
        },
    )


@login_required(login_url="/login/")
@require_POST
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    experience.delete()

    if wants_json(request):
        return JsonResponse({"message": "Pengalaman berhasil dihapus."})

    messages.success(request, "Pengalaman berhasil dihapus!")
    return redirect("main:show_experience")


@login_required(login_url="/login/")
@require_POST
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if experience.starred_by.filter(pk=request.user.pk).exists():
        experience.starred_by.remove(request.user)
        is_starred = False
    else:
        experience.starred_by.add(request.user)
        is_starred = True

    if wants_json(request):
        return JsonResponse(
            {
                "is_starred": is_starred,
                "star_count": experience.starred_by.count(),
            }
        )

    return redirect("main:show_experience")


@login_required(login_url="/login/")
@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {
                "message": (
                    "Hanya pemilik portofolio yang dapat menambahkan pengalaman."
                )
            },
            status=403,
        )

    form = ExperienceForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    experience = form.save()
    return JsonResponse(
        {
            "message": "Pengalaman berhasil ditambahkan.",
            "id": str(experience.pk),
        },
        status=201,
    )


# Authentication


def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    return render(
        request,
        "register.html",
        {"name": PORTFOLIO_OWNER, "form": form},
    )


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login",
            timezone.localtime().strftime("%Y-%m-%d %H:%M:%S %Z"),
            samesite="Lax",
        )
        return response

    return render(
        request,
        "login.html",
        {"name": PORTFOLIO_OWNER, "form": form},
    )


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response
