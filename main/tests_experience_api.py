
import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from main.models import Experience


class ExperienceAPITest(APITestCase):
    """Pengujian REST API Experience untuk empat peran."""

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner",
            password="test-password",
            email="owner@example.com",
        )

        self.regular = User.objects.create_user(
            username="regular",
            password="test-password",
        )

        self.editor = User.objects.create_user(
            username="editor",
            password="test-password",
        )
        self.editor.groups.add(
            Group.objects.create(name="Editor")
        )

        self.experience = Experience.objects.create(
            title="Mentor Agama",
            description="Membimbing mahasiswa baru",
            category="volunteer",
        )

        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse(
            "api:experience-detail",
            args=[self.experience.pk],
        )
        self.star_url = reverse(
            "api:experience-star",
            args=[self.experience.pk],
        )

        self.payload = {
            "title": "Research Assistant",
            "description": "Meneliti data pendidikan",
            "category": "research",
        }

    def test_public_list_detail_search(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data[0]["id"],
            str(self.experience.pk),
        )
        self.assertTrue(response.data[0]["is_ongoing"])
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertFalse(response.data[0]["is_starred"])

        self.assertEqual(
            self.client.get(self.detail_url).status_code, 200
        )

        response = self.client.get(
            self.list_url, {"title": "MENTOR"}
        )
        self.assertEqual(len(response.data), 1)

        response = self.client.get(
            self.list_url, {"title": "XYZ"}
        )
        self.assertEqual(response.data, [])

    def test_guest_and_regular_cannot_write(self):
        for user in (None, self.regular):
            with self.subTest(user=str(user)):
                self.client.force_authenticate(user=user)

                response = self.client.post(
                    self.list_url, self.payload, format="json"
                )
                self.assertEqual(response.status_code, 403)

                response = self.client.patch(
                    self.detail_url,
                    {"title": "Changed"},
                    format="json",
                )
                self.assertEqual(response.status_code, 403)

                response = self.client.delete(self.detail_url)
                self.assertEqual(response.status_code, 403)

        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Mentor Agama")

    def test_editor_can_edit_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(
            self.detail_url,
            {"title": "<b>Edited</b>"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Edited")

        response = self.client.post(
            self.list_url, self.payload, format="json"
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_create_update_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            self.list_url, self.payload, format="json"
        )
        self.assertEqual(response.status_code, 201)

        created_id = response.data["id"]
        created_url = reverse(
            "api:experience-detail",
            args=[created_id],
        )

        self.assertTrue(
            Experience.objects.filter(pk=created_id).exists()
        )

        response = self.client.put(
            created_url,
            {**self.payload, "title": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Experience.objects.get(pk=created_id).title,
            "Updated",
        )

        response = self.client.delete(created_url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Experience.objects.filter(pk=created_id).exists()
        )

    def test_validation_and_read_only_fields(self):
        self.client.force_authenticate(user=self.owner)

        for changes, field in [
            ({"title": "<b></b>"}, "title"),
            ({"description": "<i> </i>"}, "description"),
        ]:
            response = self.client.post(
                self.list_url,
                {**self.payload, **changes},
                format="json",
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)

        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": "<b>Clean</b>",
                "star_count": 100,
                "is_starred": True,
                "starred_by": [self.regular.pk],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Clean")
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

        created = Experience.objects.get(
            pk=response.data["id"]
        )
        self.assertFalse(created.starred_by.exists())

    def test_star_requires_login_and_toggles(self):
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=self.regular)

        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

        self.assertTrue(
            self.experience.starred_by.filter(
                pk=self.regular.pk
            ).exists()
        )

        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_missing_experience_and_wrong_method(self):
        missing_url = reverse(
            "api:experience-detail",
            args=[uuid.uuid4()],
        )

        self.assertEqual(
            self.client.get(missing_url).status_code, 404
        )

        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code, 405
        )

    def test_session_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)

        self.assertTrue(
            client.login(
                username="owner",
                password="test-password",
            )
        )

        response = client.post(
            self.list_url, self.payload, format="json"
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)

    def test_session_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)

        self.assertTrue(
            client.login(
                username="owner",
                password="test-password",
            )
        )

        page = client.get(
            self.list_url,
            HTTP_ACCEPT="text/html",
        )
        self.assertEqual(page.status_code, 200)

        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Experience.objects.count(), 2)
