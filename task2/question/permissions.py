from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        if request.user.user_group == 'moderator':
            return True
        return False


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        if request.data.get('user_id') == request.user.id:
            return True
        return False
