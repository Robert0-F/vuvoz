"""
Custom permissions for the waste paper collection service.
"""
from rest_framework import permissions


class IsAdministrator(permissions.BasePermission):
    """User must have role 'admin' (Super Admin)."""

    message = "Только администратор может выполнить это действие."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) == 'admin'


class IsCompanyUser(permissions.BasePermission):
    """User must have role 'company'."""

    message = "Only collection company users can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) == 'company'


class IsCompanyOrAdmin(permissions.BasePermission):
    """User must have role 'company' or 'admin'."""

    message = "Только компания или администратор может выполнить это действие."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) in ('company', 'admin')


class IsInstitutionUser(permissions.BasePermission):
    """User must have role 'institution'."""

    message = "Only institution users can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) == 'institution'


class IsOwnCompany(permissions.BasePermission):
    """Company can only access their own CompanyProfile; admin can access any."""

    message = "You can only access your own company profile."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) in ('company', 'admin')

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'role', None) == 'admin':
            return True
        return obj.user == request.user


class IsParentCompany(permissions.BasePermission):
    """Company can only access institutions where parent_company == user.company_profile; admin any."""

    message = "You can only access institutions belonging to your company."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) in ('company', 'admin')

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'role', None) == 'admin':
            return True
        if not hasattr(request.user, 'company_profile'):
            return False
        return obj.parent_company == request.user.company_profile


class IsOwnInstitution(permissions.BasePermission):
    """Institution can only access their own InstitutionProfile."""

    message = "You can only access your own institution profile."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) == 'institution'

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsInstitutionAccess(permissions.BasePermission):
    """
    Admin: full access. Company: institution if parent_company == user.company_profile.
    Institution: only their own institution.
    """

    message = "You do not have access to this institution."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'role', None) in ('admin', 'company', 'institution')

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'role', None) == 'admin':
            return True
        if getattr(request.user, 'role', None) == 'company':
            return (
                hasattr(request.user, 'company_profile')
                and obj.parent_company == request.user.company_profile
            )
        if getattr(request.user, 'role', None) == 'institution':
            return obj.user == request.user
        return False


class CanViewRequest(permissions.BasePermission):
    """
    Admin: full access. Company: request.receiving_company == user.company_profile.
    Institution: request.institution == user.institution_profile.
    """

    message = "You can only view collection requests you are associated with."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, 'role', None)
        return role in ('admin', 'company', 'institution')

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'role', None) == 'admin':
            return True
        if getattr(request.user, 'role', None) == 'company':
            return (
                hasattr(request.user, 'company_profile')
                and obj.receiving_company == request.user.company_profile
            )
        if getattr(request.user, 'role', None) == 'institution':
            return (
                hasattr(request.user, 'institution_profile')
                and obj.institution == request.user.institution_profile
            )
        return False
