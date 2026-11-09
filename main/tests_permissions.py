
from types import SimpleNamespace

from django.contrib.auth.models import (
    AnonymousUser, Group, User
)
from django.test import TestCase
from rest_framework.permissions import IsAuthenticated

from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly


class ExperiencePermissionTests(TestCase):

    def setUp(self):
        self.guest = AnonymousUser()

        self.regular = User.objects.create_user(
            username="regular",
            password="test-password",
        )

        self.editor = User.objects.create_user(
            username="editor",
            password="test-password",
        )

        group = Group.objects.create(name="Editor")
        self.editor.groups.add(group)

        self.owner = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="test-password",
        )

    def test_experience_permissions(self):
        permission = IsPortfolioOwnerOrEditorOrReadOnly()

        roles = [
            self.guest,
            self.regular,
            self.editor,
            self.owner,
        ]

        expected = {
            "GET":    [True, True, True, True],
            "POST":   [False, False, False, True],
            "PUT":    [False, False, True, True],
            "PATCH":  [False, False, True, True],
            "DELETE": [False, False, False, True],
        }

        for method, results in expected.items():
            for user, allowed in zip(roles, results):
                with self.subTest(method=method, user=str(user)):
                    request = SimpleNamespace(
                        method=method,
                        user=user,
                    )

                    self.assertEqual(
                        permission.has_permission(request, None),
                        allowed,
                    )

    def test_star_requires_authentication(self):
        permission = IsAuthenticated()

        for user, allowed in [
            (self.guest, False),
            (self.regular, True),
            (self.editor, True),
            (self.owner, True),
        ]:
            with self.subTest(user=str(user)):
                request = SimpleNamespace(
                    method="POST",
                    user=user,
                )

                self.assertEqual(
                    permission.has_permission(request, None),
                    allowed,
                )
