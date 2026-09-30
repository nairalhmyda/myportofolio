from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied    
from main.forms import ProjectForm  
from django.views.decorators.http import require_POST  
import datetime

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project

def is_editor(user):
    return (
        user.is_authenticated
        and user.groups.filter(name="Editor").exists()
    )

from django.shortcuts import get_object_or_404, render, redirect
from main.forms import ProjectForm


def show_projects(request):
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Naira Al Humayda",
        "title_query": title_query,
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)


def show_experience(request):
    json_response = get_experiences_json(request)

    experiences = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    experiences = [
        experience.object
        for experience in experiences
    ]

    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Naira Al Humayda",
        "experience_list": experiences,
        "title_query": title_query,
        "is_editor": is_editor(request.user),
    }

    return render(request, "experience.html", context)

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Pengalaman baru berhasil ditambahkan!",
        )
        return redirect("main:show_experience")

    context = {
        "name": "Naira Al Humayda",
        "form": form,
        "page_title": "Tambah Pengalaman",
        "submit_label": "Tambah Pengalaman",
    }

    return render(
        request,
        "experience_form.html",
        context,
    )



@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not request.user.is_superuser and not is_editor(request.user):
        raise PermissionDenied

    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )

    form = ExperienceForm(
        request.POST or None,
        instance=experience,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Pengalaman berhasil diperbarui!",
        )
        return redirect("main:show_experience")

    context = {
        "name": "Naira Al Humayda",
        "form": form,
        "page_title": "Edit Pengalaman",
        "submit_label": "Simpan Perubahan",
        "experience": experience,
    }

    return render(
        request,
        "experience_form.html",
        context,
    )

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(
        Experience,
        pk=experience_id,
    )

    if request.method == "POST":
        experience.delete()
        messages.success(
            request,
            "Pengalaman berhasil dihapus!",
        )
        return redirect("main:show_experience")

    return redirect("main:show_experience")

def get_experiences_json(request):
    title_query = request.GET.get("title", "").strip()

    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(
            title__icontains=title_query
        )

    experiences_json = serializers.serialize(
        "json",
        experiences,
    )

    return HttpResponse(
        experiences_json,
        content_type="application/json",
    )

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Proyek baru berhasil ditambahkan!",
        )
        return redirect("main:show_projects")

    context = {
        "name": "Naira Al Humayda",
        "form": form,
    }

    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def update_project(request, project_id):
    if not request.user.is_superuser and not is_editor(request.user):
        raise PermissionDenied

    project = get_object_or_404(
        Project,
        pk=project_id,
    )

    form = ProjectForm(
        request.POST or None,
        instance=project,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Proyek berhasil diperbarui!",
        )
        return redirect("main:show_projects")

    context = {
        "name": "Naira Al Humayda",
        "form": form,
        "page_title": "Edit Project",
        "submit_label": "Simpan Perubahan",
        "project": project,
    }

    return render(
        request,
        "projects_form.html",
        context,
    )


from django.http import JsonResponse

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(
        Project,
        pk=project_id,
    )

    if request.method == "POST":
        project.delete()
        messages.success(
            request,
            "Proyek berhasil dihapus!",
        )
        return redirect("main:show_projects")

    return redirect("main:show_projects")

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Naira Al Humayda",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    return redirect("main:show_main")

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)