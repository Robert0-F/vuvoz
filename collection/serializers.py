import secrets

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import (
    CollectionRequest,
    CompanyProfile,
    InAppNotification,
    InstitutionProfile,
    NewsArticle,
    PriceList,
    RequestMaterialLine,
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

    class Meta:
        model = InstitutionProfile
        fields = [
            'id',
            'parent_company',
            'parent_company_name',
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

    class Meta:
        model = InstitutionProfile
        fields = [
            'parent_company',
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
        req = self.context.get('request')
        if parent_company is not None and req and getattr(req.user, 'role', None) == 'admin':
            instance.parent_company = parent_company
        email = validated_data.get('email')
        if email is not None:
            instance.user.username = email.strip().lower()
            instance.user.email = email.strip().lower()
            instance.user.save(update_fields=['username', 'email'])
        return super().update(instance, validated_data)


class MaterialLineSerializer(serializers.Serializer):
    """One material type + weight for request create."""

    material_type = serializers.ChoiceField(
        choices=[c[0] for c in CollectionRequest.MaterialType.choices]
    )
    amount_kg = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount_kg(self, value):
        return validate_paper_weight_kg(value)


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
    material_type_display = serializers.CharField(
        source='get_material_type_display', read_only=True
    )
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

    def get_material_lines(self, instance):
        lines = list(
            instance.material_lines.values('material_type', 'amount_kg').order_by('id')
        )
        return [
            {'material_type': l['material_type'], 'amount_kg': str(l['amount_kg'])}
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
    requests_by_status = serializers.DictField(child=serializers.IntegerField())
    total_weight_all_time = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    total_weight_this_month = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )


class PriceListSerializer(serializers.ModelSerializer):
    """CRUD for PriceList (admin only)."""

    material_type_display = serializers.CharField(
        source='get_material_type_display', read_only=True
    )

    class Meta:
        model = PriceList
        fields = [
            'id',
            'material_type',
            'material_type_display',
            'price_per_kg',
            'valid_from',
            'valid_to',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['created_at']


class CurrentPricesSerializer(serializers.Serializer):
    """Read-only current prices per material type for frontend calculation."""

    material_type = serializers.CharField()
    material_type_display = serializers.CharField()
    price_per_kg = serializers.DecimalField(max_digits=10, decimal_places=2)


class CollectionRequestCompleteSerializer(serializers.Serializer):
    """Payload for completing a request (company only)."""

    actual_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=True
    )
    actual_collection_date = serializers.DateField(required=False, allow_null=True)
    internal_notes = serializers.CharField(required=False, allow_blank=True)

    def validate_actual_amount(self, value):
        return validate_paper_weight_kg(value)


class CalculatePreviewSerializer(serializers.Serializer):
    """Request for price calculation preview. Single line or multi-line."""

    material_type = serializers.ChoiceField(
        choices=[c[0] for c in CollectionRequest.MaterialType.choices],
        required=False,
    )
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
