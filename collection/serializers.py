import secrets

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import (
    AuditLog,
    BonusConfig,
    CollectionRequest,
    CompanyProfile,
    InstitutionBonus,
    InstitutionRegistrationRequest,
    InAppNotification,
    InstitutionProfile,
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
    RequestMaterialLine,
    SupportChatMessage,
    SupportConfig,
)
from .validators import (
    validate_email_format,
    validate_inn,
    validate_kpp,
    validate_ogrn,
    validate_paper_weight_kg,
    validate_phone_ru,
)

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Minimal user info and role."""

    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display']


class CompanyProfileSerializer(serializers.ModelSerializer):
    """Serializer for CompanyProfile (list, retrieve, update)."""

    password = serializers.CharField(
        max_length=128,
        required=False,
        allow_blank=True,
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = CompanyProfile
        fields = [
            'id',
            'company_name',
            'address',
            'contact_phone',
            'contact_email',
            'legal_address',
            'inn',
            'kpp',
            'ogrn',
            'bank_account',
            'bank_name',
            'bik',
            'corr_account',
            'website',
            'logo',
            'description',
            'created_at',
            'password',
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)
        return data

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password and password.strip():
            instance.user.set_password(password.strip())
            instance.user.save(update_fields=['password'])
        return super().update(instance, validated_data)

    def validate_inn(self, value):
        return validate_inn(value or '')

    def validate_kpp(self, value):
        return validate_kpp(value or '')

    def validate_ogrn(self, value):
        return validate_ogrn(value or '')

    def validate_contact_phone(self, value):
        return validate_phone_ru(value or '')


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Create company (admin only). Creates User (role=company) + CompanyProfile."""

    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(
        max_length=128,
        required=False,
        allow_blank=True,
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = CompanyProfile
        fields = [
            'email',
            'password',
            'company_name',
            'address',
            'contact_phone',
            'contact_email',
            'legal_address',
            'inn',
            'kpp',
            'ogrn',
            'bank_account',
            'bank_name',
            'bik',
            'corr_account',
            'website',
            'description',
        ]

    def validate_email(self, value):
        value = validate_email_format(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с такой почтой уже существует.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с такой почтой (логином) уже существует.")
        return value

    def validate_inn(self, value):
        return validate_inn(value or '')

    def validate_kpp(self, value):
        return validate_kpp(value or '')

    def validate_ogrn(self, value):
        return validate_ogrn(value or '')

    def validate_contact_phone(self, value):
        return validate_phone_ru(value or '')

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop('email').strip().lower()
        password = validated_data.pop('password', None) or ''
        if not password.strip():
            password = secrets.token_urlsafe(12)
        user = User(
            username=email,
            email=email,
            role=User.Role.COMPANY,
            is_active=True,
        )
        user.set_password(password)
        user.save()
        return CompanyProfile.objects.create(user=user, **validated_data)


class InstitutionProfileSerializer(serializers.ModelSerializer):
    """Serializer for InstitutionProfile (list, retrieve, update)."""

    parent_company_name = serializers.CharField(
        source='parent_company.company_name', read_only=True
    )
    parent_company_contact_phone = serializers.CharField(
        source='parent_company.contact_phone', read_only=True, default=''
    )
    parent_company_contact_email = serializers.EmailField(
        source='parent_company.contact_email', read_only=True, default=''
    )
    support_user = serializers.PrimaryKeyRelatedField(read_only=True)
    support_username = serializers.CharField(source='support_user.username', read_only=True, default='')
    support_unread_count = serializers.SerializerMethodField()

    def get_support_unread_count(self, obj):
        return SupportChatMessage.objects.filter(
            institution=obj,
            is_read=False,
            sender__role=User.Role.SUPPORT,
        ).count()

    class Meta:
        model = InstitutionProfile
        fields = [
            'id',
            'parent_company',
            'parent_company_name',
            'parent_company_contact_phone',
            'parent_company_contact_email',
            'support_user',
            'support_username',
            'support_unread_count',
            'institution_name',
            'address',
            'contact_person',
            'phone',
            'email',
            'institution_type',
            'bonus_balance',
            'legal_address',
            'inn',
            'kpp',
            'contact_person_on_site',
            'phone_on_site',
            'preferred_days',
            'preferred_hours',
            'access_details',
            'container_location',
            'company_notes',
            'created_at',
        ]
        read_only_fields = ['id', 'parent_company', 'created_at']

    def validate_inn(self, value):
        return validate_inn(value or '')

    def validate_kpp(self, value):
        return validate_kpp(value or '')


class InstitutionCreateSerializer(serializers.ModelSerializer):
    """
    Create institution (company or admin). Creates User with username=email, optional password.
    Admin can pass parent_company; company uses own profile.
    Response includes credentials (username, password) only on create.
    """

    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(
        max_length=128,
        required=False,
        allow_blank=True,
        write_only=True,
        style={'input_type': 'password'},
    )
    parent_company = serializers.PrimaryKeyRelatedField(
        queryset=CompanyProfile.objects.all(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = InstitutionProfile
        fields = [
            'email',
            'password',
            'parent_company',
            'institution_name',
            'address',
            'contact_person',
            'phone',
            'institution_type',
        ]

    def validate_email(self, value):
        value = validate_email_format(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с такой почтой уже существует.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с такой почтой (логином) уже существует.")
        return value

    def validate_phone(self, value):
        return validate_phone_ru(value or '')

    def validate(self, attrs):
        required = ['institution_name', 'address', 'contact_person', 'email']
        for field in required:
            if not (attrs.get(field) or '').strip():
                raise serializers.ValidationError({field: "Обязательное поле."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop('email').strip().lower()
        password = validated_data.pop('password', None) or ''
        if not password.strip():
            password = secrets.token_urlsafe(12)

        parent_company = validated_data.pop('parent_company', None)
        if parent_company is None and self.context.get('request'):
            if getattr(self.context['request'].user, 'role', None) == 'admin':
                raise serializers.ValidationError(
                    {'parent_company': 'Для администратора необходимо указать компанию.'}
                )
            parent_company = self.context['request'].user.company_profile

        user = User(
            username=email,
            email=email,
            role=User.Role.INSTITUTION,
            is_active=True,
        )
        user.set_password(password)
        user.save()

        institution = InstitutionProfile.objects.create(
            user=user,
            parent_company=parent_company,
            email=email,
            **validated_data,
        )

        self.context['created_credentials'] = {
            'username': email,
            'password': password,
        }
        from .signals import institution_created
        institution_created.send(
            sender=InstitutionProfile,
            instance=institution,
            password=password,
            email=email,
        )
        return institution


class InstitutionUpdateSerializer(serializers.ModelSerializer):
    """Update institution (partial). Admin can change parent_company, email (login), password."""

    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        max_length=128,
        required=False,
        allow_blank=True,
        write_only=True,
        style={'input_type': 'password'},
    )
    parent_company = serializers.PrimaryKeyRelatedField(
        queryset=CompanyProfile.objects.all(),
        required=False,
    )
    support_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.SUPPORT),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = InstitutionProfile
        fields = [
            'parent_company',
            'support_user',
            'institution_name',
            'address',
            'contact_person',
            'phone',
            'email',
            'institution_type',
            'legal_address',
            'inn',
            'kpp',
            'contact_person_on_site',
            'phone_on_site',
            'preferred_days',
            'preferred_hours',
            'access_details',
            'container_location',
            'company_notes',
            'password',
        ]

    def validate_email(self, value):
        if not value:
            return value
        value = validate_email_format(value)
        user = self.instance.user
        if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Пользователь с такой почтой уже существует.")
        if User.objects.filter(username__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Пользователь с такой почтой (логином) уже существует.")
        return value

    def validate_phone(self, value):
        return validate_phone_ru(value or '')

    def validate_inn(self, value):
        return validate_inn(value or '')

    def validate_kpp(self, value):
        return validate_kpp(value or '')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password and password.strip():
            instance.user.set_password(password.strip())
            instance.user.save(update_fields=['password'])
        parent_company = validated_data.pop('parent_company', None)
        support_user = validated_data.pop('support_user', serializers.empty)
        req = self.context.get('request')
        if parent_company is not None and req and getattr(req.user, 'role', None) == 'admin':
            instance.parent_company = parent_company
        if support_user is not serializers.empty and req and getattr(req.user, 'role', None) == 'admin':
            instance.support_user = support_user
        email = validated_data.get('email')
        if email is not None:
            instance.user.username = email.strip().lower()
            instance.user.email = email.strip().lower()
            instance.user.save(update_fields=['username', 'email'])
        return super().update(instance, validated_data)


class MaterialLineSerializer(serializers.Serializer):
    """One material type (code) + weight for request create."""

    material_type = serializers.CharField(max_length=32)
    amount_kg = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount_kg(self, value):
        return validate_paper_weight_kg(value)

    def validate_material_type(self, value):
        if not Material.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError(
                f'Материал с кодом "{value}" не найден или не активен.'
            )
        return value


class CollectionRequestCreateSerializer(serializers.Serializer):
    """Create request with material_lines (multiple material types + weights)."""

    material_lines = serializers.ListField(
        child=MaterialLineSerializer(),
        allow_empty=False,
        min_length=1,
    )
    desired_date = serializers.DateField(required=False, allow_null=True)
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate_material_lines(self, value):
        from .models import RequestWeightLimit
        total = sum(line['amount_kg'] for line in value)
        if total <= 0:
            raise serializers.ValidationError('Суммарный вес должен быть больше 0.')
        min_kg, max_kg = RequestWeightLimit.get_limits()
        if total < min_kg:
            raise serializers.ValidationError(f'Суммарный вес не менее {min_kg} кг.')
        if total > max_kg:
            raise serializers.ValidationError(f'Суммарный вес не более {max_kg} кг.')
        return value


class CollectionRequestSerializer(serializers.ModelSerializer):
    """Serializer for CollectionRequest. Notes/internal_notes visible only to company/admin."""

    institution_name = serializers.CharField(
        source='institution.institution_name', read_only=True
    )
    receiving_company_name = serializers.CharField(
        source='receiving_company.company_name', read_only=True
    )
    receiving_company_phone = serializers.SerializerMethodField()
    receiving_company_email = serializers.SerializerMethodField()

    def get_receiving_company_phone(self, obj):
        company = getattr(obj, 'receiving_company', None)
        return getattr(company, 'contact_phone', None) or '' if company else ''

    def get_receiving_company_email(self, obj):
        company = getattr(obj, 'receiving_company', None)
        return getattr(company, 'contact_email', None) or '' if company else ''
    material_type_display = serializers.SerializerMethodField()
    material_lines = serializers.SerializerMethodField()

    class Meta:
        model = CollectionRequest
        fields = [
            'id',
            'request_number',
            'institution',
            'institution_name',
            'receiving_company',
            'receiving_company_name',
            'receiving_company_phone',
            'receiving_company_email',
            'status',
            'urgency',
            'material_type',
            'material_type_display',
            'material_lines',
            'paper_weight_kg',
            'estimated_amount',
            'actual_amount',
            'estimated_value',
            'actual_value',
            'desired_date',
            'estimated_collection_date',
            'actual_collection_date',
            'comment',
            'notes',
            'internal_notes',
            'created_at',
            'completed_at',
        ]
        read_only_fields = [
            'id', 'request_number', 'institution', 'receiving_company',
            'estimated_value', 'actual_value',
            'created_at', 'completed_at',
        ]
        extra_kwargs = {'paper_weight_kg': {'required': False}}

    def get_material_type_display(self, obj):
        return Material.get_display_name(obj.material_type)

    def get_material_lines(self, instance):
        lines = list(
            instance.material_lines.select_related('material').values(
                'material__code', 'material__name', 'amount_kg'
            ).order_by('id')
        )
        return [
            {
                'material_type': l['material__code'],
                'material_type_display': l['material__name'] or l['material__code'],
                'amount_kg': str(l['amount_kg']),
            }
            for l in lines
        ]

    def validate_paper_weight_kg(self, value):
        if value is None:
            return value
        return validate_paper_weight_kg(value)

    def validate_estimated_amount(self, value):
        return validate_paper_weight_kg(value)

    def validate_actual_amount(self, value):
        if value is None:
            return value
        return validate_paper_weight_kg(value)

    def validate(self, attrs):
        request = self.context.get('request')
        role = getattr(request.user, 'role', None) if request else None
        if role not in ('company', 'admin'):
            attrs.pop('notes', None)
            attrs.pop('estimated_collection_date', None)
            attrs.pop('internal_notes', None)
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        role = getattr(request.user, 'role', None) if request else None
        if role not in ('company', 'admin'):
            data.pop('notes', None)
            data.pop('internal_notes', None)
        return data


class CompanyStatsSerializer(serializers.Serializer):
    """Response format for /api/stats/company/."""

    total_institutions = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    requests_by_status = serializers.DictField(child=serializers.IntegerField())
    total_weight_kg = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    recent_requests = CollectionRequestSerializer(many=True, read_only=True)
    monthly_comparison = serializers.DictField(required=False)
    weight_by_institution_type = serializers.DictField(required=False)
    avg_processing_time_hours = serializers.FloatField(required=False)


class CompanyDashboardSerializer(serializers.Serializer):
    """Response for /api/stats/company/dashboard/ – KPIs, monthly weights, material breakdown."""

    new_requests = serializers.IntegerField()
    active_requests = serializers.IntegerField()
    completed_this_month = serializers.IntegerField()
    weight_kg_this_month = serializers.FloatField()
    institutions_count = serializers.IntegerField()
    monthly_weights = serializers.ListField(
        child=serializers.DictField(),
        help_text='List of { month: YYYY-MM, weight_kg } for last 12 months',
    )
    material_breakdown = serializers.ListField(
        child=serializers.DictField(),
        help_text='List of { material_type, material_type_display, weight_kg }',
    )
    requests_by_status = serializers.DictField(child=serializers.IntegerField())
    selected_month = serializers.CharField(required=False)
    month_start = serializers.CharField(required=False)
    month_end = serializers.CharField(required=False)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InAppNotification
        fields = ['id', 'title', 'message', 'link', 'read', 'created_at']


class NewsArticleSerializer(serializers.ModelSerializer):
    """Serializer for NewsArticle. Public list/retrieve; admin CRUD."""

    author_username = serializers.CharField(source='author.username', read_only=True, default='')
    excerpt = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id',
            'title',
            'content',
            'excerpt',
            'image',
            'image_url',
            'created_at',
            'is_published',
            'author',
            'author_username',
        ]
        read_only_fields = ['created_at']

    def get_excerpt(self, obj):
        if not obj.content:
            return ''
        return obj.content[:200] + '...' if len(obj.content) > 200 else obj.content

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class InstitutionStatsSerializer(serializers.Serializer):
    """Response format for /api/stats/institution/."""

    total_requests = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField(required=False, default=0)
    completion_rate_percent = serializers.FloatField(required=False, default=0)
    requests_by_status = serializers.DictField(child=serializers.IntegerField())
    total_weight_all_time = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    total_weight_period = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    total_earnings_period = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    avg_weight_per_request = serializers.FloatField(required=False, default=0)
    bonus_balance = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False, required=False, default=0
    )
    bonus_points_period = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False, required=False, default=0
    )
    points_spent_period = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False, required=False, default=0
    )
    period_start = serializers.DateField(allow_null=True)
    period_end = serializers.DateField(allow_null=True)
    material_breakdown = serializers.ListField(child=serializers.DictField())
    monthly_series = serializers.ListField(child=serializers.DictField(), required=False, default=list)
    previous_period = serializers.DictField(required=False, default=dict)


class AdminStatsSerializer(serializers.Serializer):
    """Response format for /api/stats/admin/. All collections in date range."""

    materials = serializers.ListField(
        child=serializers.DictField(),
        help_text='By material_type: total_kg, request_count, material_type_display',
    )
    top_organizations = serializers.ListField(
        child=serializers.DictField(),
        help_text='institution_name, institution_id, total_kg, request_count',
    )
    requests_by_status = serializers.ListField(
        child=serializers.DictField(),
        help_text='status, status_display, count',
    )
    weight_over_time = serializers.ListField(
        child=serializers.DictField(),
        help_text='period_label, date_start, total_kg',
    )


def _material_media_url(file_field):
    if not file_field or not file_field.name:
        return None
    url = file_field.url
    if url and not url.startswith('/'):
        url = '/' + url.lstrip('/')
    return url or None


class MaterialSerializer(serializers.ModelSerializer):
    """CRUD for Material (admin). Extensible material types for prices and requests."""

    image_url = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()
    clear_image = serializers.BooleanField(write_only=True, required=False, default=False)
    clear_icon_image = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Material
        fields = [
            'id',
            'name',
            'code',
            'short_description',
            'icon_image',
            'icon_url',
            'image',
            'image_url',
            'icon',
            'sort_order',
            'is_active',
            'clear_image',
            'clear_icon_image',
        ]
        read_only_fields = ['image_url', 'icon_url']
        extra_kwargs = {
            'icon_image': {'write_only': True},
            'image': {'write_only': True},
        }

    def get_image_url(self, obj):
        return _material_media_url(obj.image)

    def get_icon_url(self, obj):
        return _material_media_url(obj.icon_image)

    def _coerce_bool(self, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).lower() in ('1', 'true', 'yes', 'on')

    def _apply_media_updates(self, instance, validated_data):
        from .services.media_service import process_material_icon, process_material_photo

        clear_image = self._coerce_bool(validated_data.pop('clear_image', False))
        clear_icon_image = self._coerce_bool(validated_data.pop('clear_icon_image', False))
        icon_upload = validated_data.pop('icon_image', serializers.empty)
        image_upload = validated_data.pop('image', serializers.empty)

        if clear_icon_image and instance.icon_image:
            instance.icon_image.delete(save=False)
            instance.icon_image = None
        if icon_upload is not serializers.empty and icon_upload:
            if instance.icon_image:
                instance.icon_image.delete(save=False)
            processed_icon = process_material_icon(icon_upload)
            instance.icon_image.save(processed_icon.name, processed_icon, save=False)

        if clear_image and instance.image:
            instance.image.delete(save=False)
            instance.image = None
        if image_upload is not serializers.empty and image_upload:
            if instance.image:
                instance.image.delete(save=False)
            processed = process_material_photo(image_upload)
            instance.image.save(processed.name, processed, save=False)

        return instance

    def create(self, validated_data):
        validated_data = dict(validated_data)
        clear_image = validated_data.pop('clear_image', False)
        clear_icon_image = validated_data.pop('clear_icon_image', False)
        icon_upload = validated_data.pop('icon_image', None)
        image_upload = validated_data.pop('image', None)
        instance = Material.objects.create(**validated_data)
        patch_data = {}
        if icon_upload:
            patch_data['icon_image'] = icon_upload
        if image_upload:
            patch_data['image'] = image_upload
        if clear_image:
            patch_data['clear_image'] = clear_image
        if clear_icon_image:
            patch_data['clear_icon_image'] = clear_icon_image
        if patch_data:
            self._apply_media_updates(instance, patch_data)
            instance.save()
        return instance

    def update(self, instance, validated_data):
        validated_data = dict(validated_data)
        instance = self._apply_media_updates(instance, validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PublicMaterialSerializer(serializers.Serializer):
    """Public catalog: material with current price."""

    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    short_description = serializers.CharField()
    icon = serializers.CharField()
    icon_url = serializers.CharField(allow_null=True)
    image_url = serializers.CharField(allow_null=True)
    price_per_kg = serializers.DecimalField(max_digits=10, decimal_places=2)
    sort_order = serializers.IntegerField()


class PublicPickupLineItemSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()
    weight_kg = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class PublicPickupRequestLineSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    material_code = serializers.CharField(source='material.code', read_only=True)

    class Meta:
        model = PublicPickupRequestLine
        fields = [
            'id',
            'material',
            'material_name',
            'material_code',
            'weight_kg',
            'line_payout',
        ]
        read_only_fields = fields


class PublicPickupRequestCreateSerializer(serializers.Serializer):
    items = PublicPickupLineItemSerializer(many=True)
    phone = serializers.CharField(max_length=50)
    address = serializers.CharField()
    preferred_date = serializers.DateField()
    contact_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Добавьте хотя бы один вид сырья.')
        material_ids = [item['material_id'] for item in value]
        if len(material_ids) != len(set(material_ids)):
            raise serializers.ValidationError('Один материал нельзя указать дважды.')
        return value

    def validate_preferred_date(self, value):
        from django.utils import timezone

        if value < timezone.now().date():
            raise serializers.ValidationError('Дата вывоза не может быть в прошлом.')
        return value

    def validate(self, attrs):
        from .models import RequestWeightLimit

        items = attrs.get('items') or []
        min_kg, max_kg = RequestWeightLimit.get_limits()
        for item in items:
            material = Material.objects.filter(pk=item['material_id'], is_active=True).first()
            if not material:
                raise serializers.ValidationError({'items': 'Материал не найден или неактивен.'})
            price = PriceList.objects.filter(material=material, is_active=True).first()
            if not price:
                raise serializers.ValidationError(
                    {'items': f'Для материала «{material.name}» не задана цена.'}
                )
            weight_kg = item['weight_kg']
            if weight_kg < min_kg or weight_kg > max_kg:
                raise serializers.ValidationError(
                    {'items': f'Вес для «{material.name}» должен быть от {min_kg} до {max_kg} кг.'}
                )
        return attrs

    def _resolve_line(self, material_id, weight_kg):
        from decimal import Decimal

        material = Material.objects.filter(pk=material_id, is_active=True).first()
        price = PriceList.objects.filter(material=material, is_active=True).first()
        line_payout = (weight_kg * price.price_per_kg).quantize(Decimal('0.01'))
        return material, weight_kg, line_payout

    def create(self, validated_data):
        from decimal import Decimal

        items_data = validated_data.pop('items')
        resolved = [self._resolve_line(i['material_id'], i['weight_kg']) for i in items_data]
        total_payout = sum((r[2] for r in resolved), Decimal('0')).quantize(Decimal('0.01'))
        request = PublicPickupRequest.objects.create(
            estimated_payout=total_payout,
            phone=validated_data['phone'].strip(),
            address=validated_data['address'].strip(),
            preferred_date=validated_data['preferred_date'],
            contact_name=(validated_data.get('contact_name') or '').strip(),
        )
        PublicPickupRequestLine.objects.bulk_create([
            PublicPickupRequestLine(
                request=request,
                material=material,
                weight_kg=weight_kg,
                line_payout=line_payout,
            )
            for material, weight_kg, line_payout in resolved
        ])
        return request


class PublicPickupRequestAdminSerializer(serializers.ModelSerializer):
    lines = PublicPickupRequestLineSerializer(many=True, read_only=True)
    materials_summary = serializers.SerializerMethodField()
    total_weight_kg = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PublicPickupRequest
        fields = [
            'id',
            'contact_name',
            'phone',
            'address',
            'preferred_date',
            'lines',
            'materials_summary',
            'total_weight_kg',
            'estimated_payout',
            'status',
            'status_display',
            'admin_notes',
            'created_at',
        ]
        read_only_fields = [
            'contact_name',
            'phone',
            'address',
            'preferred_date',
            'lines',
            'materials_summary',
            'total_weight_kg',
            'estimated_payout',
            'created_at',
            'status_display',
        ]

    def get_materials_summary(self, obj):
        parts = []
        for line in obj.lines.all():
            parts.append(f'{line.material.name} {line.weight_kg} кг')
        return ', '.join(parts) if parts else '—'

    def get_total_weight_kg(self, obj):
        from decimal import Decimal
        total = sum((line.weight_kg for line in obj.lines.all()), Decimal('0'))
        return str(total)


class CompanyRegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyRegistrationRequest
        fields = [
            'id',
            'company_name',
            'contact_name',
            'phone',
            'email',
            'address',
            'comment',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PriceListSerializer(serializers.ModelSerializer):
    """CRUD for PriceList (admin only). One record per material (unique)."""

    material_name = serializers.CharField(source='material.name', read_only=True)
    material_code = serializers.CharField(source='material.code', read_only=True)
    price_per_kg = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = PriceList
        fields = [
            'id',
            'material',
            'material_code',
            'material_name',
            'price_per_kg',
            'valid_from',
            'valid_to',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def validate_material(self, value):
        if self.instance is None and PriceList.objects.filter(material=value).exists():
            raise serializers.ValidationError('Цена для этого материала уже существует.')
        return value


class CurrentPricesSerializer(serializers.Serializer):
    """Read-only current prices per material type for frontend calculation."""

    material_type = serializers.CharField()
    material_type_display = serializers.CharField()
    price_per_kg = serializers.DecimalField(max_digits=10, decimal_places=2)


class CollectionRequestCompleteSerializer(serializers.Serializer):
    """Payload for completing a request (company only).
    Either actual_amount (single total kg) or actual_material_lines (per-material actual weights).
    When multiple materials in the request, use actual_material_lines to specify weight per type.
    """

    actual_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    actual_material_lines = serializers.ListField(
        child=MaterialLineSerializer(),
        required=False,
        allow_empty=False,
    )
    actual_collection_date = serializers.DateField(required=False, allow_null=True)
    internal_notes = serializers.CharField(required=False, allow_blank=True)

    def validate_actual_amount(self, value):
        return validate_paper_weight_kg(value)

    def validate(self, attrs):
        has_amount = attrs.get('actual_amount') is not None
        has_lines = attrs.get('actual_material_lines')
        if has_lines:
            if not attrs['actual_material_lines']:
                raise serializers.ValidationError(
                    {'actual_material_lines': 'Укажите хотя бы одну строку с фактическим весом по типу сырья.'}
                )
            return attrs
        if has_amount:
            return attrs
        raise serializers.ValidationError(
            'Укажите actual_amount (общий вес в кг) или actual_material_lines (фактический вес по каждому типу сырья).'
        )


class CalculatePreviewSerializer(serializers.Serializer):
    """Request for price calculation preview. Single line or multi-line."""

    material_type = serializers.CharField(max_length=32, required=False)
    amount_kg = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        required=False,
    )
    material_lines = MaterialLineSerializer(many=True, required=False)

    def validate_amount_kg(self, value):
        return validate_paper_weight_kg(value)

    def validate(self, attrs):
        if attrs.get('material_lines'):
            if not attrs['material_lines']:
                raise serializers.ValidationError({'material_lines': 'Минимум одна строка.'})
            return attrs
        if attrs.get('material_type') is not None and attrs.get('amount_kg') is not None:
            return attrs
        raise serializers.ValidationError(
            'Укажите material_type и amount_kg или material_lines.'
        )


class BonusConfigSerializer(serializers.ModelSerializer):
    """Single global bonus percent. Admin only."""

    class Meta:
        model = BonusConfig
        fields = ['id', 'bonus_percent']


class InstitutionBonusSerializer(serializers.ModelSerializer):
    """Bonus for an institution from a completed request. Admin: list, retrieve, update awarded_amount and confirm."""

    institution_name = serializers.CharField(source='institution.institution_name', read_only=True)
    request_number = serializers.CharField(source='collection_request.request_number', read_only=True)
    order_value = serializers.SerializerMethodField()

    def get_order_value(self, obj):
        req = obj.collection_request
        val = req.actual_value or req.estimated_value
        return str(val) if val is not None else None

    class Meta:
        model = InstitutionBonus
        fields = [
            'id',
            'collection_request',
            'institution',
            'institution_name',
            'request_number',
            'order_value',
            'calculated_amount',
            'awarded_amount',
            'status',
            'confirmed_at',
            'confirmed_by',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'collection_request',
            'institution',
            'institution_name',
            'request_number',
            'order_value',
            'calculated_amount',
            'created_at',
        ]


class ProductCategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'sort_order', 'is_active', 'product_count']

    def get_product_count(self, obj):
        return getattr(obj, 'product_count', obj.products.filter(is_active=True).count())


class ProductCategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'sort_order', 'is_active']
        extra_kwargs = {'slug': {'required': False, 'allow_blank': True}}

    def validate_slug(self, value):
        from django.utils.text import slugify
        if not value:
            return value
        slug = slugify(value, allow_unicode=True)
        if not slug:
            raise serializers.ValidationError('Некорректный slug.')
        return slug

    def validate(self, attrs):
        from django.utils.text import slugify
        if not attrs.get('slug') and attrs.get('name'):
            attrs['slug'] = slugify(attrs['name'], allow_unicode=True)
        if not attrs.get('slug'):
            raise serializers.ValidationError({'slug': 'Укажите slug или название.'})
        return attrs


class ProductSerializer(serializers.ModelSerializer):
    """Product for points catalog. Admin: CRUD. Institution: read-only list."""
    image_url = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'category_slug',
            'name', 'description', 'image', 'image_url',
            'price_in_points', 'is_active', 'created_at',
        ]
        read_only_fields = ['image_url', 'category_name', 'category_slug']
        extra_kwargs = {
            'image': {'write_only': True},
        }

    def get_image_url(self, obj):
        if not obj.image or not obj.image.name:
            return None
        url = obj.image.url
        if url and not url.startswith('/'):
            url = '/' + url.lstrip('/')
        return url or None


class PublicProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    price_in_points = serializers.DecimalField(max_digits=10, decimal_places=2)
    image_url = serializers.CharField(allow_null=True)
    category_id = serializers.IntegerField(allow_null=True)
    category_name = serializers.CharField(allow_null=True)
    category_slug = serializers.CharField(allow_null=True)


class PointsOrderLineSerializer(serializers.ModelSerializer):
    """Line in a points order."""
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = PointsOrderLine
        fields = ['id', 'product', 'product_name', 'quantity', 'price_at_order']


class PointsOrderSerializer(serializers.ModelSerializer):
    """Order placed with green points."""
    lines = PointsOrderLineSerializer(many=True, read_only=True)
    institution_name = serializers.CharField(source='institution.institution_name', read_only=True)

    class Meta:
        model = PointsOrder
        fields = [
            'id', 'institution', 'institution_name', 'status',
            'recipient_name', 'recipient_phone', 'address',
            'total_points', 'created_at', 'lines',
        ]
        read_only_fields = ['id', 'institution', 'institution_name', 'total_points', 'created_at', 'lines']


class PointsOrderStatusSerializer(serializers.ModelSerializer):
    """Admin: update order status only (accepted, completed, cancelled)."""

    class Meta:
        model = PointsOrder
        fields = ['status']


class PointsOrderCreateSerializer(serializers.Serializer):
    """Create order: delivery info + list of { product_id, quantity }."""
    recipient_name = serializers.CharField(max_length=255)
    recipient_phone = serializers.CharField(max_length=50)
    address = serializers.CharField(style={'base_template': 'textarea.html'})
    items = serializers.ListField(
        child=serializers.DictField(),
        help_text='List of { "product_id": int, "quantity": int }',
    )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Выберите хотя бы один товар.')
        for i, item in enumerate(value):
            if not isinstance(item.get('product_id'), int) or not isinstance(item.get('quantity'), int):
                raise serializers.ValidationError(f'Строка {i + 1}: укажите product_id и quantity (целые числа).')
            if item['quantity'] < 1:
                raise serializers.ValidationError(f'Строка {i + 1}: количество должно быть не менее 1.')
        return value


class InstitutionRegistrationRequestSerializer(serializers.ModelSerializer):
    """Public submission from homepage; admin lists these."""
    email = serializers.EmailField(required=True)

    class Meta:
        model = InstitutionRegistrationRequest
        fields = ['id', 'first_name', 'patronymic', 'institution_name', 'address', 'phone', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'created_at',
            'category',
            'action_type',
            'actor_role',
            'actor_username',
            'target_model',
            'target_id',
            'short_summary',
            'ip_address',
        ]

    def get_actor_username(self, obj):
        if obj.actor:
            return obj.actor.username
        return ''


class SupportConfigSerializer(serializers.ModelSerializer):
    support_username = serializers.CharField(source='support_user.username', read_only=True, default='')
    support_email = serializers.EmailField(source='support_user.email', read_only=True, default='')
    institutions_assigned = serializers.SerializerMethodField()

    class Meta:
        model = SupportConfig
        fields = ['id', 'support_user', 'support_username', 'support_email', 'institutions_assigned']

    def get_institutions_assigned(self, obj):
        if not obj.support_user_id:
            return 0
        return InstitutionProfile.objects.filter(support_user_id=obj.support_user_id).count()


class SupportUserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, max_length=128, write_only=True, required=False, allow_blank=True)

    def validate_email(self, value):
        value = validate_email_format(value)
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        if User.objects.filter(role=User.Role.SUPPORT).exists():
            raise serializers.ValidationError('Аккаунт техподдержки уже создан. Можно только один.')
        return value.lower()

    def create(self, validated_data):
        import secrets
        email = validated_data['email']
        password = (validated_data.get('password') or '').strip() or secrets.token_urlsafe(10)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            role=User.Role.SUPPORT,
        )
        config = SupportConfig.objects.first()
        if not config:
            config = SupportConfig.objects.create()
        config.support_user = user
        config.save(update_fields=['support_user'])
        config.assign_to_all_institutions()
        return user


class SupportUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'date_joined']


class SupportAssignedInstitutionSerializer(serializers.ModelSerializer):
    unread_count = serializers.IntegerField(read_only=True, default=0)
    last_message_at = serializers.DateTimeField(read_only=True, allow_null=True)
    last_message_preview = serializers.CharField(read_only=True, allow_blank=True, default='')

    class Meta:
        model = InstitutionProfile
        fields = [
            'id', 'institution_name', 'address', 'contact_person', 'phone', 'email',
            'unread_count', 'last_message_at', 'last_message_preview',
        ]


class SupportChatMessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    sender_role = serializers.CharField(source='sender.role', read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = SupportChatMessage
        fields = [
            'id',
            'institution',
            'sender',
            'sender_username',
            'sender_role',
            'message',
            'is_read',
            'is_mine',
            'created_at',
        ]
        read_only_fields = ['id', 'sender', 'sender_username', 'sender_role', 'is_read', 'is_mine', 'created_at']

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.sender_id == request.user.id
