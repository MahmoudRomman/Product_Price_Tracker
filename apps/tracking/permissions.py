from rest_framework import permissions

class IsAdminOrOwner(permissions.BasePermission):
    """
    Only admin and tracked_product owner can edit or delete the tracked_product
    but anyone can get any link
    """
    def has_object_permission(self, request, view, obj):
        # Safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # only product link owner or admin can make (PUT, PATCH, DELETE)
        return request.user.is_staff or (obj.user == request.user)