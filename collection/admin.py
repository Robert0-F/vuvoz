from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
from django.utils.html import format_html

from .models import (
    BonusConfig,
    AuditLog,
    CollectionRequest,
    CompanyProfile,
    CustomUser,
    InstitutionBonus,
    InstitutionProfile,
    InstitutionRegistrationRequest,
    InAppNotification,
    Material,
    PublicPickupRequest,
    PublicPickupRequestLine,
    CompanyRegistrationRequest,
    NewsArticle,
    PointsOrder,
    PointsOrderLine,
    PriceList,
    Product,
    ProductCategory,
    RequestWeightLimit,
    SupportChatMessage,
    SupportConfig,
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
        'support_user',
        'institution_type',
        'contact_person',
        'email',
        'created_at',
    )
    list_filter = ('institution_type', 'parent_company', 'support_user', 'created_at')
    search_fields = ('institution_name', 'contact_person', 'email')
    raw_id_fields = ('user', 'parent_company', 'support_user')
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


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('sort_order', 'name')
    readonly_fields = ('icon_preview', 'photo_preview')
    fieldsets = (
        (None, {'fields': ('name', 'code', 'short_description', 'sort_order', 'is_active')}),
        ('Иконка (главная, калькулятор)', {'fields': ('icon_image', 'icon_preview', 'icon')}),
        ('Фото (каталог сырья)', {'fields': ('image', 'photo_preview')}),
    )

    @admin.display(description='Превью иконки')
    def icon_preview(self, obj):
        if obj.icon_image:
            return format_html('<img src="{}" width="96" height="96" style="object-fit:contain" />', obj.icon_image.url)
        return '—'

    @admin.display(description='Превью фото')
    def photo_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" style="max-height:140px;object-fit:cover" />', obj.image.url)
        return '—'


class PublicPickupRequestLineInline(admin.TabularInline):
    model = PublicPickupRequestLine
    extra = 0
    readonly_fields = ('material', 'weight_kg', 'line_payout')


@admin.register(PublicPickupRequest)
class PublicPickupRequestAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'estimated_payout',
        'phone',
        'preferred_date',
        'status',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('phone', 'address', 'contact_name')
    readonly_fields = ('created_at', 'estimated_payout')
    inlines = [PublicPickupRequestLineInline]


@admin.register(CompanyRegistrationRequest)
class CompanyRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'contact_name', 'phone', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('company_name', 'contact_name', 'phone', 'email')


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ('material', 'price_per_kg', 'valid_from', 'valid_to', 'is_active', 'created_at')
    list_filter = ('material', 'is_active', 'valid_from')
    search_fields = ('material__name', 'material__code')
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


@admin.register(SupportConfig)
class SupportConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'support_user')
    raw_id_fields = ('support_user',)


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


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price_in_points', 'is_active', 'image', 'created_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('category', 'name', 'description', 'price_in_points', 'is_active')}),
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


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'colored_category',
        'action_type',
        'actor',
        'actor_role',
        'target_model',
        'target_id',
        'short_summary',
    )
    list_filter = ('category', 'actor_role', 'action_type', 'target_model', 'created_at')
    search_fields = ('short_summary', 'action_type', 'target_model', 'target_id', 'actor__username', 'actor__email')
    readonly_fields = (
        'created_at',
        'actor',
        'actor_role',
        'action_type',
        'category',
        'target_model',
        'target_id',
        'short_summary',
        'payload_json',
        'ip_address',
        'user_agent',
    )
    actions = ('export_as_txt', 'export_as_csv')

    @admin.display(description='Категория')
    def colored_category(self, obj):
        color = {
            'info': '#2563eb',
            'warning': '#d97706',
            'critical': '#dc2626',
        }.get(obj.category, '#374151')
        return format_html(
            '<span style="font-weight:600;color:{};">{}</span>',
            color,
            obj.get_category_display(),
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='Экспорт выбранных записей в TXT')
    def export_as_txt(self, request, queryset):
        response = HttpResponse(content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=audit_logs.txt'
        for item in queryset.order_by('-created_at'):
            response.write(
                f'[{item.created_at:%Y-%m-%d %H:%M:%S}] '
                f'[{item.category}] [{item.action_type}] '
                f'actor={item.actor_id or "-"} role={item.actor_role or "-"} '
                f'target={item.target_model}:{item.target_id} '
                f'summary="{item.short_summary}"\n'
            )
        return response

    @admin.action(description='Экспорт выбранных записей в CSV')
    def export_as_csv(self, request, queryset):
        import csv

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=audit_logs.csv'
        writer = csv.writer(response)
        writer.writerow([
            'created_at', 'category', 'action_type', 'actor_id', 'actor_role',
            'target_model', 'target_id', 'short_summary', 'ip_address', 'user_agent',
        ])
        for item in queryset.order_by('-created_at'):
            writer.writerow([
                item.created_at.isoformat(),
                item.category,
                item.action_type,
                item.actor_id or '',
                item.actor_role,
                item.target_model,
                item.target_id,
                item.short_summary,
                item.ip_address,
                item.user_agent,
            ])
        return response


@admin.register(SupportChatMessage)
class SupportChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'institution', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'institution')
    search_fields = ('institution__institution_name', 'sender__username', 'message')
    raw_id_fields = ('institution', 'sender')
    readonly_fields = ('created_at',)
