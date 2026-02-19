import secrets
from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Avg, Case, Count, DurationField, ExpressionWrapper, F, Q, Sum, When
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone as tz
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BonusConfig,
    CollectionRequest,
    CompanyProfile,
    InstitutionBonus,
    InstitutionProfile,
    InstitutionRegistrationRequest,
    InAppNotification,
    NewsArticle,
    PointsOrder,
    PointsOrderLine,
    PriceList,
    Product,
    RequestMaterialLine,
    RequestWeightLimit,
)
from .permissions import (
    CanViewRequest,
    IsAdministrator,
    IsCompanyOrAdmin,
    IsCompanyUser,
    IsInstitutionAccess,
    IsInstitutionUser,
    IsOwnCompany,
)
from .serializers import (
    AdminStatsSerializer,
    BonusConfigSerializer,
    CalculatePreviewSerializer,
    CollectionRequestCompleteSerializer,
    CollectionRequestCreateSerializer,
    CompanyCreateSerializer,
    CompanyProfileSerializer,
    CompanyStatsSerializer,
    CollectionRequestSerializer,
    InstitutionBonusSerializer,
    InstitutionCreateSerializer,
    InstitutionProfileSerializer,
    InstitutionStatsSerializer,
    InstitutionUpdateSerializer,
    NewsArticleSerializer,
    NotificationSerializer,
    PointsOrderCreateSerializer,
    PointsOrderSerializer,
    PointsOrderStatusSerializer,
    PriceListSerializer,
    ProductSerializer,
    InstitutionRegistrationRequestSerializer,
    UserBasicSerializer,
)


class HealthView(APIView):
    """GET /api/health/ — no auth. Use to check that Django is responding."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'ok'})


class CompanyProfileViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    List, retrieve, update. Company: own profile only. Admin: all companies, create, delete.
    """
    serializer_class = CompanyProfileSerializer

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [IsAuthenticated(), IsAdministrator()]
        return [IsAuthenticated(), IsOwnCompany()]

    def get_queryset(self):
        if getattr(self.request.user, 'role', None) == 'admin':
            return CompanyProfile.objects.all()
        return CompanyProfile.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CompanyCreateSerializer
        return CompanyProfileSerializer


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
        if getattr(user, 'role', None) == 'admin':
            qs = InstitutionProfile.objects.all()
        elif getattr(user, 'role', None) == 'company' and hasattr(user, 'company_profile'):
            qs = InstitutionProfile.objects.filter(parent_company=user.company_profile)
        elif getattr(user, 'role', None) == 'institution' and hasattr(user, 'institution_profile'):
            qs = InstitutionProfile.objects.filter(user=user)
        else:
            return InstitutionProfile.objects.none()
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(institution_name__icontains=search)
                | Q(institution_type__icontains=search)
                | Q(contact_person__icontains=search)
                | Q(email__icontains=search)
            )
        return qs.select_related('parent_company')

    def get_serializer_class(self):
        if self.action == 'create':
            return InstitutionCreateSerializer
        if self.action in ('update', 'partial_update'):
            return InstitutionUpdateSerializer
        return InstitutionProfileSerializer

    def get_permissions(self):
        perms = [IsAuthenticated, IsInstitutionAccess]
        if self.action in ('create', 'destroy'):
            perms.append(IsCompanyOrAdmin)
        if self.action == 'reset_password':
            perms.append(IsCompanyUser)
        return [p() for p in perms]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['is_admin'] = getattr(self.request.user, 'role', None) == 'admin'
        return context

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
    Create: institution users only; uses material_lines (multiple material types + weights).
    List/Retrieve: filtered by user role (company sees received, institution sees own).
    Update: only company users can update (e.g. status).
    """
    serializer_class = CollectionRequestSerializer
    permission_classes = [IsAuthenticated, CanViewRequest]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'admin':
            qs = CollectionRequest.objects.all()
        elif getattr(user, 'role', None) == 'company' and hasattr(user, 'company_profile'):
            qs = CollectionRequest.objects.filter(receiving_company=user.company_profile)
        elif getattr(user, 'role', None) == 'institution' and hasattr(user, 'institution_profile'):
            qs = CollectionRequest.objects.filter(institution=user.institution_profile)
        else:
            return CollectionRequest.objects.none()
        qs = qs.select_related('institution', 'receiving_company')
        status = self.request.query_params.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)
        start_date = _parse_date_param(self.request.query_params.get('start_date'))
        end_date = _parse_date_param(self.request.query_params.get('end_date'))
        qs = _apply_date_filter(qs, start_date, end_date)
        itype = self.request.query_params.get('institution_type', '').strip()
        if itype:
            qs = qs.filter(institution__institution_type__icontains=itype)
        min_kg = self.request.query_params.get('min_weight')
        if min_kg is not None:
            try:
                qs = qs.filter(paper_weight_kg__gte=Decimal(str(min_kg)))
            except Exception:
                pass
        max_kg = self.request.query_params.get('max_weight')
        if max_kg is not None:
            try:
                qs = qs.filter(paper_weight_kg__lte=Decimal(str(max_kg)))
            except Exception:
                pass
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return CollectionRequestCreateSerializer
        return CollectionRequestSerializer

    def get_permissions(self):
        perms = [IsAuthenticated]
        if self.action == 'create':
            perms.append(IsInstitutionUser)
        else:
            perms.append(CanViewRequest)
        if self.action in ('update', 'partial_update', 'complete'):
            perms.append(IsCompanyUser)
        return [p() for p in perms]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        institution = request.user.institution_profile
        validated = serializer.validated_data
        material_lines = validated['material_lines']
        total_kg = sum(line['amount_kg'] for line in material_lines)
        req = CollectionRequest.objects.create(
            institution=institution,
            paper_weight_kg=total_kg,
            desired_date=validated.get('desired_date'),
            comment=validated.get('comment') or '',
        )
        for line in material_lines:
            RequestMaterialLine.objects.create(
                collection_request=req,
                material_type=line['material_type'],
                amount_kg=line['amount_kg'],
            )
        req.save()
        return Response(
            CollectionRequestSerializer(req, context={'request': request}).data,
            status=201,
        )

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """Mark request as completed (company only). Sets actual_amount, actual_collection_date, internal_notes, actual_value.
        If actual_material_lines is provided (multiple materials), actual_amount and actual_value are computed from it.
        """
        req = self.get_object()
        if req.status == CollectionRequest.Status.COMPLETED:
            return Response(
                {'detail': 'Заявка уже завершена.'},
                status=400,
            )
        ser = CollectionRequestCompleteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        if data.get('actual_material_lines'):
            total_kg = sum(line['amount_kg'] for line in data['actual_material_lines'])
            total_value = sum(
                line['amount_kg'] * PriceList.get_current_price(line['material_type'])
                for line in data['actual_material_lines']
            )
            req.actual_amount = total_kg
            req.actual_value = total_value
        else:
            req.actual_amount = data['actual_amount']
        req.actual_collection_date = data.get('actual_collection_date')
        req.internal_notes = (data.get('internal_notes') or '').strip()
        req.status = CollectionRequest.Status.COMPLETED
        req.save()
        return Response(CollectionRequestSerializer(req, context={'request': request}).data)

    @action(detail=False, methods=['post'], url_path='calculate')
    def calculate(self, request):
        """Preview estimated value. Single: material_type+amount_kg. Multi: material_lines."""
        ser = CalculatePreviewSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        if data.get('material_lines'):
            total_value = sum(
                line['amount_kg'] * PriceList.get_current_price(line['material_type'])
                for line in data['material_lines']
            )
            total_kg = sum(line['amount_kg'] for line in data['material_lines'])
            return Response({
                'material_lines': data['material_lines'],
                'total_kg': str(total_kg),
                'estimated_value': str(total_value),
            })
        material_type = data['material_type']
        amount_kg = data['amount_kg']
        price = PriceList.get_current_price(material_type)
        value = amount_kg * price
        return Response({
            'material_type': material_type,
            'amount_kg': str(amount_kg),
            'price_per_kg': str(price),
            'estimated_value': str(value),
        })


class NewsArticleViewSet(viewsets.ModelViewSet):
    """News articles. Public: GET list/retrieve (published only). Admin: full CRUD."""

    serializer_class = NewsArticleSerializer

    def get_queryset(self):
        qs = NewsArticle.objects.all().select_related('author')
        if self.action in ('list', 'retrieve') and not (
            self.request.user.is_authenticated
            and getattr(self.request.user, 'role', None) == 'admin'
        ):
            qs = qs.filter(is_published=True)
        return qs.order_by('-created_at')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsAdministrator()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PriceListViewSet(viewsets.ModelViewSet):
    """CRUD for PriceList. Admin only. GET /current/ — current prices (any authenticated)."""
    serializer_class = PriceListSerializer
    queryset = PriceList.objects.all()
    filterset_fields = ['material_type', 'is_active']

    def get_permissions(self):
        if self.action == 'current':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdministrator()]

    @action(detail=False, methods=['get'], url_path='current')
    def current(self, request):
        from django.utils import timezone
        today = timezone.now().date()
        qs = PriceList.objects.filter(
            is_active=True,
            valid_from__lte=today,
        ).filter(Q(valid_to__isnull=True) | Q(valid_to__gte=today))
        seen = set()
        rows = []
        for p in qs.order_by('material_type', '-valid_from'):
            if p.material_type in seen:
                continue
            seen.add(p.material_type)
            rows.append({
                'material_type': p.material_type,
                'material_type_display': p.get_material_type_display(),
                'price_per_kg': str(p.price_per_kg),
            })
        return Response(rows)


class WeightLimitsView(APIView):
    """Returns min/max weight (kg) for collection requests. Authenticated."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        min_kg, max_kg = RequestWeightLimit.get_limits()
        return Response({'min_kg': str(min_kg), 'max_kg': str(max_kg)})


class BonusConfigView(APIView):
    """GET/PATCH single bonus config (bonus_percent). Admin only."""

    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        config = BonusConfig.objects.first()
        if not config:
            config = BonusConfig.objects.create(bonus_percent=Decimal('0'))
        return Response(BonusConfigSerializer(config).data)

    def patch(self, request):
        config = BonusConfig.objects.first()
        if not config:
            config = BonusConfig.objects.create(bonus_percent=Decimal('0'))
        serializer = BonusConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InstitutionBonusViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """List and manage institution bonuses. Admin only. PATCH: set awarded_amount and/or confirm (status=confirmed)."""

    permission_classes = [IsAuthenticated, IsAdministrator]
    serializer_class = InstitutionBonusSerializer
    queryset = InstitutionBonus.objects.select_related(
        'institution', 'collection_request', 'confirmed_by'
    ).order_by('-created_at')

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        institution_id = self.request.query_params.get('institution')
        if institution_id:
            qs = qs.filter(institution_id=institution_id)
        return qs

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == InstitutionBonus.Status.CONFIRMED and not instance.confirmed_at:
            instance.confirmed_at = tz.now()
            instance.confirmed_by = self.request.user
            amount = instance.awarded_amount or instance.calculated_amount or 0
            if amount > 0:
                from django.db.models import F
                InstitutionProfile.objects.filter(pk=instance.institution_id).update(
                    bonus_balance=F('bonus_balance') + amount
                )
            instance.save(update_fields=['confirmed_at', 'confirmed_by'])


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


class InstitutionPointsView(APIView):
    """GET balance and history (accruals + expenses) for current institution. Amount — date — request/order."""

    permission_classes = [IsAuthenticated, IsInstitutionUser]

    def get(self, request):
        inst = request.user.institution_profile
        balance = inst.bonus_balance
        accruals = InstitutionBonus.objects.filter(
            institution=inst, status=InstitutionBonus.Status.CONFIRMED
        ).select_related('collection_request').order_by('-confirmed_at')
        expenses = PointsOrder.objects.filter(institution=inst).order_by('-created_at')
        history = []
        for b in accruals:
            amt = b.awarded_amount or b.calculated_amount
            ref = b.collection_request.request_number or f'Заявка {b.collection_request_id}'
            history.append({
                'type': 'accrual',
                'amount': str(amt),
                'date': (b.confirmed_at or b.created_at).isoformat() if (b.confirmed_at or b.created_at) else None,
                'reference': ref,
            })
        for o in expenses:
            history.append({
                'type': 'expense',
                'amount': f'-{o.total_points}',
                'date': o.created_at.isoformat() if o.created_at else None,
                'reference': f'Заказ #{o.id}',
            })
        history.sort(key=lambda x: x['date'] or '', reverse=True)
        return Response({
            'balance': str(balance),
            'history': history[:100],
        })


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Products for points catalog. Institution: list active only. Admin: full CRUD."""

    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdministrator()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Product.objects.all()
        if getattr(self.request.user, 'role', None) != 'admin':
            qs = qs.filter(is_active=True)
        return qs.order_by('name')


class InstitutionRegistrationRequestViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Public: POST to submit registration request. Admin: list all requests."""

    serializer_class = InstitutionRegistrationRequestSerializer
    queryset = InstitutionRegistrationRequest.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdministrator()]

    def get_queryset(self):
        return InstitutionRegistrationRequest.objects.all().order_by('-created_at')


class PointsOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Orders paid with points. Institution: create + list own. Admin: list all + PATCH status."""

    serializer_class = PointsOrderSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ('partial_update', 'update'):
            return PointsOrderStatusSerializer
        if self.action == 'create':
            return PointsOrderCreateSerializer
        return PointsOrderSerializer

    def get_queryset(self):
        qs = PointsOrder.objects.prefetch_related('lines__product').select_related('institution')
        if getattr(self.request.user, 'role', None) != 'admin':
            qs = qs.filter(institution__user=self.request.user)
        return qs.order_by('-created_at')

    def perform_update(self, serializer):
        if getattr(self.request.user, 'role', None) != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Только администратор может менять статус заказа.')
        serializer.save()

    def create(self, request, *args, **kwargs):
        if getattr(request.user, 'role', None) != 'institution':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Только организация может оформлять заказы на баллы.')
        inst = request.user.institution_profile
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        items = data['items']
        total = Decimal('0')
        line_data = []
        for item in items:
            try:
                product = Product.objects.get(pk=item['product_id'], is_active=True)
            except Product.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'items': f'Товар id={item["product_id"]} не найден или не активен.'})
            qty = item['quantity']
            price = product.price_in_points
            total += price * qty
            line_data.append({'product': product, 'quantity': qty, 'price_at_order': price})
        if total > inst.bonus_balance:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'detail': f'Недостаточно баллов. Баланс: {inst.bonus_balance}, нужно: {total}.',
            })
        from django.db import transaction
        with transaction.atomic():
            order = PointsOrder.objects.create(
                institution=inst,
                status=PointsOrder.Status.PENDING,
                recipient_name=data['recipient_name'],
                recipient_phone=data['recipient_phone'],
                address=data['address'],
                total_points=total,
            )
            for ld in line_data:
                PointsOrderLine.objects.create(
                    order=order,
                    product=ld['product'],
                    quantity=ld['quantity'],
                    price_at_order=ld['price_at_order'],
                )
            InstitutionProfile.objects.filter(pk=inst.pk).update(bonus_balance=F('bonus_balance') - total)
        return Response(
            PointsOrderSerializer(order).data,
            status=201,
        )


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


def _apply_date_filter_by_field(queryset, start_date, end_date, date_field='created_at'):
    """Apply start_date/end_date to a queryset by date field (e.g. created_at or completed_at)."""
    if start_date:
        queryset = queryset.filter(**{f'{date_field}__date__gte': start_date})
    if end_date:
        queryset = queryset.filter(**{f'{date_field}__date__lte': end_date})
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
        recent_requests = requests_base.order_by('-created_at')[:10]

        # monthly_comparison: current month vs previous month
        now = tz.now()
        cur_month = requests_base.filter(
            created_at__year=now.year, created_at__month=now.month
        )
        prev_month_start = (now.replace(day=1) - __import__('datetime').timedelta(days=1)).replace(day=1)
        prev_month = requests_base.filter(
            created_at__year=prev_month_start.year,
            created_at__month=prev_month_start.month,
        )
        cur_weight = cur_month.filter(status=CollectionRequest.Status.COMPLETED).aggregate(
            t=Sum('paper_weight_kg')
        )['t'] or Decimal('0')
        prev_weight = prev_month.filter(status=CollectionRequest.Status.COMPLETED).aggregate(
            t=Sum('paper_weight_kg')
        )['t'] or Decimal('0')
        monthly_comparison = {
            'current_month_requests': cur_month.count(),
            'previous_month_requests': prev_month.count(),
            'current_month_weight_kg': float(cur_weight),
            'previous_month_weight_kg': float(prev_weight),
        }

        # weight_by_institution_type
        qs = requests_base.filter(status=CollectionRequest.Status.COMPLETED).values(
            'institution__institution_type'
        ).annotate(weight=Sum('paper_weight_kg'))
        weight_by_institution_type = {item['institution__institution_type'] or 'other': float(item['weight']) for item in qs}

        # avg_processing_time_hours: from created_at to completed_at for completed
        completed = requests_base.filter(
            status=CollectionRequest.Status.COMPLETED,
            completed_at__isnull=False,
        )
        result = completed.annotate(
            delta=ExpressionWrapper(F('completed_at') - F('created_at'), output_field=DurationField())
        ).aggregate(avg=Avg('delta'))
        delta = result.get('avg')
        avg_processing_time_hours = float(delta.total_seconds() / 3600.0) if delta else None

        data = {
            'total_institutions': total_institutions,
            'total_requests': total_requests,
            'requests_by_status': requests_by_status,
            'total_weight_kg': total_weight_kg,
            'recent_requests': recent_requests,
            'monthly_comparison': monthly_comparison,
            'weight_by_institution_type': weight_by_institution_type,
            'avg_processing_time_hours': avg_processing_time_hours,
        }
        serializer = CompanyStatsSerializer(instance=data)
        return Response(serializer.data)


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """List and mark read current user's in-app notifications."""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return InAppNotification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='mark_read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save(update_fields=['read'])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'], url_path='mark_all_read')
    def mark_all_read(self, request):
        InAppNotification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({'status': 'ok'})


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


class AdminStatsView(APIView):
    """
    GET /api/stats/admin/
    Permission: IsAdministrator.
    Query params:
      date_from, date_to (YYYY-MM-DD) — period. Default: last 365 days.
      basis — 'created' (by request creation date) or 'completed' (by completed_at, completed requests only).
    Returns: materials, top_organizations, requests_by_status, weight_over_time.
    Statistics are computed from CollectionRequest and RequestMaterialLine; no separate storage.
    """

    permission_classes = [IsAuthenticated, IsAdministrator]

    def get(self, request):
        start_date = _parse_date_param(request.query_params.get('date_from'))
        end_date = _parse_date_param(request.query_params.get('date_to'))
        if not start_date or not end_date:
            end_date = tz.now().date()
            start_date = end_date - timedelta(days=365)
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        basis = (request.query_params.get('basis') or 'created').strip().lower()
        if basis not in ('created', 'completed'):
            basis = 'created'

        date_field = 'completed_at' if basis == 'completed' else 'created_at'
        requests_base = CollectionRequest.objects.all().select_related(
            'institution', 'receiving_company'
        )
        if basis == 'completed':
            requests_base = requests_base.filter(
                status=CollectionRequest.Status.COMPLETED,
                completed_at__isnull=False,
            )
        requests_filtered = _apply_date_filter_by_field(
            requests_base, start_date, end_date, date_field
        )

        material_choices = dict(CollectionRequest.MaterialType.choices)

        # 1) Materials: from RequestMaterialLine + requests with no lines (use request.material_type + paper_weight_kg)
        lines_qs = RequestMaterialLine.objects.filter(
            collection_request__in=requests_filtered,
        ).values('material_type').annotate(
            total_kg=Sum('amount_kg'),
            request_count=Count('collection_request_id', distinct=True),
        )
        materials_by_type = {}
        for row in lines_qs:
            materials_by_type[row['material_type']] = {
                'total_kg': float(row['total_kg'] or 0),
                'request_count': row['request_count'],
            }
        # Requests with zero material_lines: add their material_type and paper_weight_kg
        from django.db.models import Exists, OuterRef
        has_lines = RequestMaterialLine.objects.filter(collection_request_id=OuterRef('pk'))
        requests_no_lines = requests_filtered.filter(~Exists(has_lines)).values(
            'material_type', 'paper_weight_kg'
        )
        for row in requests_no_lines:
            mt = row['material_type'] or 'paper'
            kg = float(row['paper_weight_kg'] or 0)
            if mt not in materials_by_type:
                materials_by_type[mt] = {'total_kg': 0, 'request_count': 0}
            materials_by_type[mt]['total_kg'] += kg
            materials_by_type[mt]['request_count'] += 1
        materials = [
            {
                'material_type': mt,
                'material_type_display': material_choices.get(mt, mt),
                'total_kg': materials_by_type[mt]['total_kg'],
                'request_count': materials_by_type[mt]['request_count'],
            }
            for mt in sorted(materials_by_type.keys(), key=lambda x: -materials_by_type[x]['total_kg'])
        ]

        # 2) Top organizations
        top_qs = requests_filtered.values(
            'institution_id', 'institution__institution_name'
        ).annotate(
            total_kg=Sum('paper_weight_kg'),
            request_count=Count('id'),
        ).order_by('-total_kg')[:30]
        top_organizations = [
            {
                'institution_id': row['institution_id'],
                'institution_name': row['institution__institution_name'] or '—',
                'total_kg': float(row['total_kg'] or 0),
                'request_count': row['request_count'],
            }
            for row in top_qs
        ]

        # 3) Requests by status
        status_agg = _requests_by_status_aggregate(requests_filtered)
        status_labels = {'new': 'Новые', 'accepted': 'Принятые', 'completed': 'Завершённые'}
        requests_by_status = [
            {'status': k, 'status_display': status_labels.get(k, k), 'count': status_agg[k]}
            for k in ('new', 'accepted', 'completed')
        ]

        # 4) Weight over time: group by week or month using the same date field
        range_days = (end_date - start_date).days
        if range_days <= 31:
            trunc_fn = TruncDate
            date_format = '%d.%m'
        elif range_days <= 93:
            trunc_fn = TruncWeek
            date_format = '%d.%m'
        else:
            trunc_fn = TruncMonth
            date_format = '%b %Y'
        weight_qs = requests_filtered.annotate(
            period=trunc_fn(date_field)
        ).values('period').annotate(total_kg=Sum('paper_weight_kg')).order_by('period')
        weight_over_time = []
        for row in weight_qs:
            if row['period']:
                label = row['period'].strftime(date_format) if hasattr(row['period'], 'strftime') else str(row['period'])
                weight_over_time.append({
                    'period_label': label,
                    'date_start': row['period'].isoformat() if hasattr(row['period'], 'isoformat') else str(row['period']),
                    'total_kg': float(row['total_kg'] or 0),
                })

        data = {
            'materials': materials,
            'top_organizations': top_organizations,
            'requests_by_status': requests_by_status,
            'weight_over_time': weight_over_time,
        }
        serializer = AdminStatsSerializer(instance=data)
        return Response(serializer.data)
