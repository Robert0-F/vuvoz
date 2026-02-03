import secrets

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import CollectionRequest, CompanyProfile, InstitutionProfile

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Minimal user info and role."""

    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display']


class CompanyProfileSerializer(serializers.ModelSerializer):
    """Serializer for CompanyProfile (list, retrieve, update)."""

    class Meta:
        model = CompanyProfile
        fields = [
            'id',
            'company_name',
            'address',
            'contact_phone',
            'contact_email',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


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
            'created_at',
        ]
        read_only_fields = ['id', 'parent_company', 'created_at']


class InstitutionCreateSerializer(serializers.ModelSerializer):
    """
    Create institution (company only). Creates User with username=email, optional password.
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

    class Meta:
        model = InstitutionProfile
        fields = [
            'email',
            'password',
            'institution_name',
            'address',
            'contact_person',
            'phone',
            'institution_type',
        ]

    def validate_email(self, value):
        value = (value or '').strip().lower()
        if not value:
            raise serializers.ValidationError("Email is required.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this email (username) already exists.")
        return value

    def validate(self, attrs):
        required = ['institution_name', 'address', 'contact_person', 'email']
        for field in required:
            if not (attrs.get(field) or '').strip():
                raise serializers.ValidationError({field: "This field is required."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        email = validated_data.pop('email').strip().lower()
        password = validated_data.pop('password', None) or ''
        if not password.strip():
            password = secrets.token_urlsafe(12)

        parent_company = self.context['request'].user.company_profile

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            role=User.Role.INSTITUTION,
            is_active=True,
        )

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
    """Update institution (partial). No user/parent_company changes. Syncs email to User."""

    class Meta:
        model = InstitutionProfile
        fields = [
            'institution_name',
            'address',
            'contact_person',
            'phone',
            'email',
            'institution_type',
        ]

    def validate_email(self, value):
        value = (value or '').strip().lower()
        if not value:
            raise serializers.ValidationError("Email is required.")
        user = self.instance.user
        if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if User.objects.filter(username__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email (username) already exists.")
        return value

    def update(self, instance, validated_data):
        email = validated_data.get('email')
        if email is not None:
            instance.user.username = email
            instance.user.email = email
            instance.user.save(update_fields=['username', 'email'])
        return super().update(instance, validated_data)


class CollectionRequestSerializer(serializers.ModelSerializer):
    """Serializer for CollectionRequest."""

    institution_name = serializers.CharField(
        source='institution.institution_name', read_only=True
    )
    receiving_company_name = serializers.CharField(
        source='receiving_company.company_name', read_only=True
    )

    class Meta:
        model = CollectionRequest
        fields = [
            'id',
            'institution',
            'institution_name',
            'receiving_company',
            'receiving_company_name',
            'status',
            'paper_weight_kg',
            'desired_date',
            'comment',
            'created_at',
        ]
        read_only_fields = ['id', 'institution', 'receiving_company', 'created_at']


class CompanyStatsSerializer(serializers.Serializer):
    """Response format for /api/stats/company/."""

    total_institutions = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    requests_by_status = serializers.DictField(child=serializers.IntegerField())
    total_weight_kg = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    recent_requests = CollectionRequestSerializer(many=True, read_only=True)


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
