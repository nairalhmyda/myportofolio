from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from main.models import Experience, Project


JSON_HEADERS = {
    "HTTP_ACCEPT": "application/json",
    "HTTP_X_REQUESTED_WITH": "XMLHttpRequest",
}


class PortfolioPageTests(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Staff of Human Community BEM Fasilkom UI",
            description="Kegiatan pengabdian masyarakat.",
            category="part-time",
        )
        self.project = Project.objects.create(
            title="Web Ilmi-FUKI",
            description="Website resources untuk PACIL.",
            tech_stack="Django, React",
            github_url="https://github.com/FUKI-Fasilkom/web-ilmi-fe",
            year=2026,
        )

    def test_main_page_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_dynamic_pages_are_accessible(self):
        projects = self.client.get(reverse("main:show_projects"))
        experiences = self.client.get(reverse("main:show_experience"))

        self.assertEqual(projects.status_code, 200)
        self.assertEqual(experiences.status_code, 200)
        self.assertContains(projects, reverse("main:get_projects_json"))
        self.assertContains(experiences, reverse("main:get_experiences_json"))

    def test_project_api_returns_frontend_contract(self):
        response = self.client.get(reverse("main:get_projects_json"))
        payload = response.json()
        item = payload["items"][0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(item["title"], self.project.title)
        self.assertEqual(item["github_url"], self.project.github_url)
        self.assertIn("urls", item)
        self.assertFalse(payload["permissions"]["can_star"])

    def test_experience_api_returns_frontend_contract(self):
        response = self.client.get(reverse("main:get_experiences_json"))
        payload = response.json()
        item = payload["items"][0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(item["title"], self.experience.title)
        self.assertEqual(item["category_display"], "Part-Time")
        self.assertTrue(item["is_ongoing"])

    def test_project_api_search(self):
        Project.objects.create(
            title="Unrelated Project",
            description="Other",
            tech_stack="Python",
            year=2025,
        )
        response = self.client.get(
            reverse("main:get_projects_json"),
            {"title": "Ilmi"},
        )
        items = response.json()["items"]

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], self.project.title)


class AjaxInteractionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            password="strong-pass-123",
            email="owner@example.com",
        )
        self.regular = User.objects.create_user(
            username="regular",
            password="strong-pass-123",
        )
        self.editor = User.objects.create_user(
            username="editor",
            password="strong-pass-123",
        )
        editor_group = Group.objects.create(name="Editor")
        self.editor.groups.add(editor_group)

        self.project = Project.objects.create(
            title="Portfolio",
            description="Project description",
            tech_stack="Django",
            github_url="https://github.com/example/portfolio",
            year=2026,
        )
        self.experience = Experience.objects.create(
            title="Research Assistant",
            description="Research experience",
            category="research",
        )

    def test_superuser_can_create_project_via_ajax(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "title": "<b>New Project</b>",
                "description": "<script>alert(1)</script>Safe text",
                "tech_stack": "Django",
                "github_url": "https://github.com/example/new-project",
                "year": 2026,
                "project_image_url": "",
            },
            **JSON_HEADERS,
        )

        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(pk=response.json()["id"])
        self.assertEqual(project.title, "New Project")
        self.assertNotIn("<script>", project.description)

    def test_regular_user_cannot_create_project_via_ajax(self):
        self.client.force_login(self.regular)
        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "title": "Blocked",
                "description": "Blocked",
                "tech_stack": "Django",
                "year": 2026,
            },
            **JSON_HEADERS,
        )
        self.assertEqual(response.status_code, 403)

    def test_star_project_returns_json_without_page_reload(self):
        self.client.force_login(self.regular)
        url = reverse("main:toggle_star", args=[self.project.pk])

        first = self.client.post(url, **JSON_HEADERS)
        second = self.client.post(url, **JSON_HEADERS)

        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.json()["is_starred"])
        self.assertEqual(first.json()["star_count"], 1)
        self.assertFalse(second.json()["is_starred"])
        self.assertEqual(second.json()["star_count"], 0)

    def test_star_experience_returns_json(self):
        self.client.force_login(self.regular)
        response = self.client.post(
            reverse("main:toggle_experience_star", args=[self.experience.pk]),
            **JSON_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_starred"])
        self.assertTrue(self.experience.starred_by.filter(pk=self.regular.pk).exists())

    def test_editor_can_edit_but_cannot_delete(self):
        self.client.force_login(self.editor)

        edit_response = self.client.get(
            reverse("main:update_project", args=[self.project.pk])
        )
        delete_response = self.client.post(
            reverse("main:delete_project", args=[self.project.pk]),
            **JSON_HEADERS,
        )

        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_owner_can_delete_project_via_ajax(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("main:delete_project", args=[self.project.pk]),
            **JSON_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
