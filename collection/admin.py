from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CollectionRequest, CompanyProfile, CustomUser, InstitutionProfile


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'contact_email', 'contact_phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('company_name', 'contact_email', 'contact_phone')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)


@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(admin.ModelAdmin):
    list_display = (
        'institution_name',
        'parent_company',
        'institution_type',
        'contact_person',
        'email',
        'created_at',
    )
    list_filter = ('institution_type', 'parent_company', 'created_at')
    search_fields = ('institution_name', 'contact_person', 'email')
    raw_id_fields = ('user', 'parent_company')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'company_profile'):
            return qs.filter(parent_company=request.user.company_profile)
        if hasattr(request.user, 'institution_profile'):
            return qs.filter(user=request.user)
        return qs.none()


@admin.register(CollectionRequest)
class CollectionRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'institution',
        'receiving_company',
        'status',
        'paper_weight_kg',
        'desired_date',
        'created_at',
    )
    list_filter = ('status', 'receiving_company', 'created_at')
    search_fields = ('institution__institution_name', 'comment')
    raw_id_fields = ('institution', 'receiving_company')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'company_profile'):
            return qs.filter(receiving_company=request.user.company_profile)
        if hasattr(request.user, 'institution_profile'):
            return qs.filter(institution=request.user.institution_profile)
        return qs.none()
