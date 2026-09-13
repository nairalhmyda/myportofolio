from django.shortcuts import render
from main.models import Experience, Project

def show_projects(request):
    context = {
        "name": "Naira Al Humayda",
        "project_list": Project.objects.all(),
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
    context = {
        "name": "Naira Al Humayda",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)
