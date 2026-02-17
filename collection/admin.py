from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    BonusConfig,
    CollectionRequest,
    CompanyProfile,
    CustomUser,
    InstitutionBonus,
    InstitutionProfile,
    InstitutionRegistrationRequest,
    InAppNotification,
    NewsArticle,
    PointsOrder,
    PointsOrderLine,
    PriceList,
    Product,
    RequestWeightLimit,
)


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
        'request_number',
        'id',
        'institution',
        'receiving_company',
        'status',
        'urgency',
        'material_type',
        'paper_weight_kg',
        'estimated_amount',
        'estimated_value',
        'actual_amount',
        'actual_value',
        'desired_date',
        'estimated_collection_date',
        'actual_collection_date',
        'created_at',
    )
    list_filter = ('status', 'urgency', 'material_type', 'receiving_company', 'created_at')
    search_fields = ('request_number', 'institution__institution_name', 'comment', 'internal_notes')
    raw_id_fields = ('institution', 'receiving_company')
    readonly_fields = ('created_at', 'completed_at', 'estimated_value', 'request_number')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'company_profile'):
            return qs.filter(receiving_company=request.user.company_profile)
        if hasattr(request.user, 'institution_profile'):
            return qs.filter(institution=request.user.institution_profile)
        return qs.none()


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published', 'author')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)
    readonly_fields = ('created_at',)


@admin.register(RequestWeightLimit)
class RequestWeightLimitAdmin(admin.ModelAdmin):
    list_display = ('id', 'min_kg', 'max_kg')
    list_editable = ('min_kg', 'max_kg')

    def has_add_permission(self, request):
        return not RequestWeightLimit.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ('material_type', 'price_per_kg', 'valid_from', 'valid_to', 'is_active', 'created_at')
    list_filter = ('material_type', 'is_active', 'valid_from')
    search_fields = ('material_type',)
    ordering = ('-valid_from',)


@admin.register(InAppNotification)
class InAppNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('title', 'message')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)


@admin.register(BonusConfig)
class BonusConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'bonus_percent')


@admin.register(InstitutionBonus)
class InstitutionBonusAdmin(admin.ModelAdmin):
    list_display = ('id', 'institution', 'collection_request', 'calculated_amount', 'awarded_amount', 'status', 'confirmed_at', 'confirmed_by')
    list_filter = ('status', 'created_at')
    search_fields = ('institution__institution_name', 'collection_request__request_number')
    raw_id_fields = ('institution', 'collection_request', 'confirmed_by')
    readonly_fields = ('created_at',)


@admin.register(InstitutionRegistrationRequest)
class InstitutionRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'institution_name', 'first_name', 'patronymic', 'address', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('institution_name', 'first_name', 'address', 'phone')
    readonly_fields = ('created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price_in_points', 'is_active', 'image', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('name', 'description', 'price_in_points', 'is_active')}),
        ('Фото товара', {'fields': ('image',)}),
    )


@admin.register(PointsOrder)
class PointsOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'institution', 'recipient_name', 'total_points', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient_name', 'recipient_phone', 'address')
    raw_id_fields = ('institution',)
    readonly_fields = ('created_at',)


@admin.register(PointsOrderLine)
class PointsOrderLineAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price_at_order')
    raw_id_fields = ('order', 'product')
