from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    # Only allows users with role = admin or superuser
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)


class IsEntity(BasePermission):
    # Only allows users with role = entity AND status = approved
    def has_permission(self, request, view):
        if not request.user.is_authenticated or request.user.role != 'entity':
            return False
        # Check entity is approved before allowing any action
        try:
            return request.user.entity_profile.status == 'approved'
        except Exception:
            return False


class IsDonor(BasePermission):
    # Only allows users with role = donor
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'donor'


class IsAdminOrEntity(BasePermission):
    # Allows both admin/superuser and approved entity
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        if request.user.role == 'entity':
            try:
                return request.user.entity_profile.status == 'approved'
            except Exception:
                return False
        return False
