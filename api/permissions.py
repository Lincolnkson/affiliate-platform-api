from rest_framework import permissions

class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'vendor'

class IsAffiliate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'affiliate'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'admin'

class IsProductOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_authenticated and hasattr(request.user, 'vendor_profile') and obj.vendor == request.user.vendor_profile and obj.vendor.user == request.user


class IsReviewAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_authenticated and obj.user == request.user