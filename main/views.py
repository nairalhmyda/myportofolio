from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project

from django.shortcuts import get_object_or_404, render, redirect
from main.forms import ProjectForm

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    projects = [project.object for project in projects]

    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Naira Al Humayda",
        "project_list": projects,
        "title_query": title_query,
    }

    return render(request, "projects.html", context)

def show_main(request):
    context = {
        "name": "Naira Al Humayda",
        "npm": "2506532233",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada Data Science."
        ),
    }
    return render(request, "index.html", context)


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
    }

    return render(request, "experience.html", context)

def create_experience(request):
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

def update_experience(request, experience_id):
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

def delete_experience(request, experience_id):
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

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Naira Al Humayda",
        "form": form,
    }

    return render(request, "projects_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)

    return HttpResponse(
        projects_json,
        content_type="application/json",
    )

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Proyek berhasil dihapus!")
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
        login(request, form.get_user())
        return redirect("main:show_main")

    context = {
        "name": "Naira Al Humayda",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    return redirect("main:show_main")

