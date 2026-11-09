
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPortfolioOwnerOrReadOnly(BasePermission):
    """Hanya superuser yang boleh mengubah data."""

    message = "Only the portfolio owner can modify projects."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    """Superuser memiliki akses penuh, Editor boleh mengedit."""

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if request.method in ("PUT", "PATCH"):
            return request.user.groups.filter(
                name="Editor"
            ).exists()

        return False
