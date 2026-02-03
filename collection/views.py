import secrets
from datetime import datetime
from decimal import Decimal

from django.db.models import Case, Count, Sum, When
from django.utils import timezone as tz
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CollectionRequest, CompanyProfile, InstitutionProfile
from .permissions import (
    CanViewRequest,
    IsCompanyUser,
    IsInstitutionAccess,
    IsInstitutionUser,
    IsOwnCompany,
)
from .serializers import (
    CompanyProfileSerializer,
    CompanyStatsSerializer,
    CollectionRequestSerializer,
    InstitutionCreateSerializer,
    InstitutionProfileSerializer,
    InstitutionStatsSerializer,
    InstitutionUpdateSerializer,
    UserBasicSerializer,
)


class CompanyProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    List, retrieve, update own company profile only.
    No create/delete via API.
    """
    permission_classes = [IsAuthenticated, IsCompanyUser, IsOwnCompany]
    serializer_class = CompanyProfileSerializer

    def get_queryset(self):
        return CompanyProfile.objects.filter(user=self.request.user)


class InstitutionViewSet(viewsets.ModelViewSet):
    """
    Company: CRUD for institutions where parent_company = user.company_profile.
    Institution: retrieve and update own institution only.
    Create (company only): InstitutionCreateSerializer, returns institution + credentials.
    Update: InstitutionUpdateSerializer.
    """
    permission_classes = [IsAuthenticated, IsInstitutionAccess]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'company' and hasattr(user, 'company_profile'):
            return InstitutionProfile.objects.filter(parent_company=user.company_profile)
        if getattr(user, 'role', None) == 'institution' and hasattr(user, 'institution_profile'):
            return InstitutionProfile.objects.filter(user=user)
        return InstitutionProfile.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return InstitutionCreateSerializer
        if self.action in ('update', 'partial_update'):
            return InstitutionUpdateSerializer
        return InstitutionProfileSerializer

    def get_permissions(self):
        perms = [IsAuthenticated, IsInstitutionAccess]
        if self.action in ('create', 'destroy'):
            perms.append(IsCompanyUser)
        if self.action == 'reset_password':
            perms.append(IsCompanyUser)
        return [p() for p in perms]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        data = InstitutionProfileSerializer(instance).data
        if 'created_credentials' in serializer.context:
            data['credentials'] = serializer.context['created_credentials']
        headers = self.get_success_headers(InstitutionProfileSerializer(instance).data)
        return Response(data, status=201, headers=headers)

    @action(detail=True, methods=['patch'], url_path='reset_password')
    def reset_password(self, request, pk=None):
        """Generate new password for institution user. Company only, own institutions."""
        from django.core.mail import send_mail
        from django.conf import settings

        institution = self.get_object()
        new_password = secrets.token_urlsafe(12)
        user = institution.user
        user.set_password(new_password)
        user.save(update_fields=['password'])

        send_mail(
            subject='Password reset - Waste Paper Collection',
            message=f'Your new password: {new_password}\nPlease change it after first login.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return Response({
            'message': 'Password reset successfully.',
            'new_password': new_password,
        })


class CollectionRequestViewSet(viewsets.ModelViewSet):
    """
    Create: institution users only; institution auto-set from user.institution_profile.
    List/Retrieve: filtered by user role (company sees received, institution sees own).
    Update: only company users can update (e.g. status).
    """
    serializer_class = CollectionRequestSerializer
    permission_classes = [IsAuthenticated, CanViewRequest]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'company' and hasattr(user, 'company_profile'):
            return CollectionRequest.objects.filter(receiving_company=user.company_profile)
        if getattr(user, 'role', None) == 'institution' and hasattr(user, 'institution_profile'):
            return CollectionRequest.objects.filter(institution=user.institution_profile)
        return CollectionRequest.objects.none()

    def get_permissions(self):
        perms = [IsAuthenticated]
        if self.action == 'create':
            perms.append(IsInstitutionUser)
        else:
            perms.append(CanViewRequest)
        if self.action in ('update', 'partial_update'):
            perms.append(IsCompanyUser)
        return [p() for p in perms]

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution_profile)


class CurrentUserView(APIView):
    """Returns current user info and role-specific profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserBasicSerializer(user).data
        if getattr(user, 'role', None) == 'company' and hasattr(user, 'company_profile'):
            data['profile'] = CompanyProfileSerializer(user.company_profile).data
        elif getattr(user, 'role', None) == 'institution' and hasattr(user, 'institution_profile'):
            data['profile'] = InstitutionProfileSerializer(user.institution_profile).data
        else:
            data['profile'] = None
        return Response(data)


def _parse_date_param(value):
    """Parse YYYY-MM-DD query param; return date or None if invalid."""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def _apply_date_filter(queryset, start_date, end_date):
    """Apply optional start_date/end_date to a queryset (created_at)."""
    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)
    return queryset


def _requests_by_status_aggregate(queryset):
    """Single-query conditional count by status. Returns dict with new, accepted, completed."""
    agg = queryset.aggregate(
        new=Count(Case(When(status=CollectionRequest.Status.NEW, then=1))),
        accepted=Count(Case(When(status=CollectionRequest.Status.ACCEPTED, then=1))),
        completed=Count(Case(When(status=CollectionRequest.Status.COMPLETED, then=1))),
    )
    return {k: agg[k] or 0 for k in ('new', 'accepted', 'completed')}


class CompanyStatsView(APIView):
    """
    GET /api/stats/company/
    Permission: IsCompanyUser.
    Query params: start_date, end_date (YYYY-MM-DD).
    """

    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get(self, request):
        company_profile = request.user.company_profile
        start_date = _parse_date_param(request.query_params.get('start_date'))
        end_date = _parse_date_param(request.query_params.get('end_date'))

        # Base querysets with select_related for FKs
        requests_base = CollectionRequest.objects.filter(
            receiving_company=company_profile
        ).select_related('institution', 'receiving_company')
        requests_filtered = _apply_date_filter(requests_base, start_date, end_date)

        # total_institutions: count institutions for this company
        total_institutions = InstitutionProfile.objects.filter(
            parent_company=company_profile
        ).count()

        # total_requests (date-filtered)
        total_requests = requests_filtered.count()

        # requests_by_status (date-filtered) in one query
        requests_by_status = _requests_by_status_aggregate(requests_filtered)

        # total_weight_kg: sum of paper_weight_kg for completed only (date-filtered)
        completed_qs = requests_filtered.filter(status=CollectionRequest.Status.COMPLETED)
        total_weight_result = completed_qs.aggregate(total=Sum('paper_weight_kg'))
        total_weight_kg = total_weight_result['total'] or Decimal('0.00')

        # recent_requests: last 10 with details (no date filter for "recent")
        recent_requests = (
            requests_base.order_by('-created_at')[:10]
        )

        data = {
            'total_institutions': total_institutions,
            'total_requests': total_requests,
            'requests_by_status': requests_by_status,
            'total_weight_kg': total_weight_kg,
            'recent_requests': recent_requests,
        }
        serializer = CompanyStatsSerializer(instance=data)
        return Response(serializer.data)


class InstitutionStatsView(APIView):
    """
    GET /api/stats/institution/
    Permission: IsInstitutionUser.
    Query params: start_date, end_date (YYYY-MM-DD) for total_requests and requests_by_status.
    """

    permission_classes = [IsAuthenticated, IsInstitutionUser]

    def get(self, request):
        institution_profile = request.user.institution_profile
        start_date = _parse_date_param(request.query_params.get('start_date'))
        end_date = _parse_date_param(request.query_params.get('end_date'))

        # All requests for this institution (for all_time and this_month)
        requests_all = CollectionRequest.objects.filter(
            institution=institution_profile
        ).select_related('institution', 'receiving_company')

        requests_filtered = _apply_date_filter(requests_all, start_date, end_date)

        # total_requests (date-filtered)
        total_requests = requests_filtered.count()

        # requests_by_status (date-filtered)
        requests_by_status = _requests_by_status_aggregate(requests_filtered)

        # total_weight_all_time: sum over all their requests (no date filter)
        total_weight_all_time = requests_all.aggregate(total=Sum('paper_weight_kg'))
        total_weight_all_time = total_weight_all_time['total'] or Decimal('0.00')

        # total_weight_this_month: sum for current month
        now = tz.now()
        this_month_qs = requests_all.filter(
            created_at__year=now.year,
            created_at__month=now.month,
        )
        total_weight_this_month = this_month_qs.aggregate(total=Sum('paper_weight_kg'))
        total_weight_this_month = total_weight_this_month['total'] or Decimal('0.00')

        data = {
            'total_requests': total_requests,
            'requests_by_status': requests_by_status,
            'total_weight_all_time': total_weight_all_time,
            'total_weight_this_month': total_weight_this_month,
        }
        serializer = InstitutionStatsSerializer(instance=data)
        return Response(serializer.data)
