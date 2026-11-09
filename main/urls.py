from django.urls import path

from main import views


app_name = "main"

urlpatterns = [
    path("", views.show_main, name="show_main"),
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),

    # Projects
    path("projects/", views.show_projects, name="show_projects"),
    path("projects/add/", views.create_project, name="create_project"),
    path("projects/add-ajax/", views.create_project_ajax, name="create_project_ajax"),
    path("projects/<int:project_id>/edit/", views.update_project, name="update_project"),
    path("projects/<int:project_id>/delete/", views.delete_project, name="delete_project"),
    path("projects/<int:project_id>/star/", views.toggle_star, name="toggle_star"),
    path("api/projects/", views.get_projects_json, name="get_projects_json"),

    # Experience
    path("experience/", views.show_experience, name="show_experience"),
    path("experience/add/", views.create_experience, name="create_experience"),
    path(
        "experience/add-ajax/",
        views.create_experience_ajax,
        name="create_experience_ajax",
    ),
    path(
        "experience/<uuid:experience_id>/edit/",
        views.update_experience,
        name="update_experience",
    ),
    path(
        "experience/<uuid:experience_id>/delete/",
        views.delete_experience,
        name="delete_experience",
    ),
    path(
        "experience/<uuid:experience_id>/star/",
        views.toggle_experience_star,
        name="toggle_experience_star",
    ),
    path("api/experiences/", views.get_experiences_json, name="get_experiences_json"),
]
