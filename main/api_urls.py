from django.urls import include, path
from main import api_views


app_name = "api"
urlpatterns = [
    path("projects/", api_views.project_list, name="project-list"),
    path("projects/<uuid:project_id>/", api_views.project_detail, name="project-detail"),
    path("projects/<uuid:project_id>/star/", api_views.project_star, name="project-star"),
]

urlpatterns += [
    path("api/v1/", include("main.api_urls")),
    path("api-auth/", include("rest_framework.urls")),
]