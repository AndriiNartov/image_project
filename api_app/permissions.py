from rest_framework import permissions


class CreateExpiredLinkPermission(permissions.BasePermission):
    """Checking if user has ability to generate expiry link according to his account tier"""

    message = "User's account tier does not include ability to generate expiry link"

    def has_permission(self, request, view):
        account_tier = request.user.account_tier
        has_permission = account_tier.has_ability_create_expiry_link
        return has_permission


class HasUserAccountTier(permissions.BasePermission):
    """Cheking if user was assigned an any account tier (in case of our task-via admin panel)"""

    message = "User has not been assigned an any account tier"

    def has_permission(self, request, view):
        return request.user.account_tier