from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class CustomUser(AbstractUser):
    """User model with role: Administrator, Collection Company, or Institution."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        COMPANY = 'company', 'Collection Company'
        INSTITUTION = 'institution', 'Institution'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COMPANY,
    )

    def __str__(self):
        return f"{self.get_username()} ({self.get_role_display()})"


class CompanyProfile(models.Model):
    """Profile for collection companies that create institutions and receive requests."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='company_profile',
    )
    company_name = models.CharField(max_length=255)
    address = models.TextField()
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    legal_address = models.TextField(blank=True)
    inn = models.CharField(max_length=12, blank=True)
    kpp = models.CharField(max_length=9, blank=True)
    ogrn = models.CharField(max_length=15, blank=True)
    bank_account = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=255, blank=True)
    bik = models.CharField(max_length=9, blank=True)
    corr_account = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    logo = models.FileField(upload_to='company_logos/', blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Company Profile'
        verbose_name_plural = 'Company Profiles'

    def __str__(self):
        return self.company_name


class InstitutionProfile(models.Model):
    """Profile for institutions created by a company; they submit requests to their parent company."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='institution_profile',
    )
    parent_company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='institutions',
    )
    institution_name = models.CharField(max_length=255)
    address = models.TextField()
    contact_person = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    institution_type = models.CharField(max_length=100)
    legal_address = models.TextField(blank=True)
    inn = models.CharField(max_length=12, blank=True)
    kpp = models.CharField(max_length=9, blank=True)
    contact_person_on_site = models.CharField(max_length=255, blank=True)
    phone_on_site = models.CharField(max_length=20, blank=True)
    preferred_days = models.CharField(max_length=100, blank=True)
    preferred_hours = models.CharField(max_length=100, blank=True)
    access_details = models.TextField(blank=True)
    container_location = models.TextField(blank=True)
    company_notes = models.TextField(
        blank=True,
        help_text='Заметка компании об организации (редактирует только компания)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Institution Profile'
        verbose_name_plural = 'Institution Profiles'

    def __str__(self):
        return self.institution_name


class CollectionRequest(models.Model):
    """Request from an institution to their parent company for paper collection."""

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        ACCEPTED = 'accepted', 'Accepted'
        COMPLETED = 'completed', 'Completed'

    class Urgency(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    institution = models.ForeignKey(
        InstitutionProfile,
        on_delete=models.CASCADE,
        related_name='requests',
    )
    receiving_company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='received_requests',
    )
    class MaterialType(models.TextChoices):
        PAPER = 'paper', 'Бумага'
        CARDBOARD = 'cardboard', 'Картон'
        NEWSPAPERS = 'newspapers', 'Газеты'
        MIXED = 'mixed', 'Смешанная'
        ARCHIVE = 'archive', 'Архивная'

    request_number = models.CharField(max_length=32, unique=True, blank=True, null=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    urgency = models.CharField(
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.MEDIUM,
    )
    material_type = models.CharField(
        max_length=20,
        choices=MaterialType.choices,
        default=MaterialType.PAPER,
    )
    paper_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=True,
    )
    estimated_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    actual_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False,
    )
    actual_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    desired_date = models.DateField(null=True, blank=True)
    estimated_collection_date = models.DateField(null=True, blank=True)
    actual_collection_date = models.DateField(null=True, blank=True)
    comment = models.TextField(blank=True)
    notes = models.TextField(
        blank=True,
        help_text='Internal notes for company (not visible to institution)',
    )
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Collection Request'
        verbose_name_plural = 'Collection Requests'

    def __str__(self):
        return f"{self.request_number or self.pk} - {self.institution.institution_name} ({self.paper_weight_kg} kg)"

    def save(self, *args, **kwargs):
        from decimal import Decimal
        from django.db.models import Max
        from django.utils import timezone

        if self.institution_id and not self.receiving_company_id:
            self.receiving_company = self.institution.parent_company
        if not self.request_number:
            today = timezone.now().date()
            prefix = f'REQ-{today:%Y%m%d}-'
            last = (
                CollectionRequest.objects.filter(request_number__startswith=prefix)
                .aggregate(Max('request_number'))
            ).get('request_number__max')
            num = int(last.split('-')[-1]) + 1 if last else 1
            self.request_number = f'{prefix}{num:04d}'
        if self.estimated_amount == 0 and self.paper_weight_kg:
            self.estimated_amount = self.paper_weight_kg
        if self.pk:
            lines = list(self.material_lines.values('material_type', 'amount_kg'))
            if lines:
                total_kg = sum(l['amount_kg'] for l in lines)
                self.estimated_amount = total_kg
                self.paper_weight_kg = total_kg
                self.estimated_value = sum(
                    l['amount_kg'] * PriceList.get_current_price(l['material_type']) for l in lines
                )
                if not self.material_type or self.material_type == 'paper':
                    self.material_type = lines[0]['material_type'] if len(lines) == 1 else 'mixed'
        elif self.material_type and self.estimated_amount is not None:
            price = PriceList.get_current_price(self.material_type)
            self.estimated_value = self.estimated_amount * price
        if self.status == CollectionRequest.Status.COMPLETED:
            if not self.completed_at:
                self.completed_at = timezone.now()
            if self.actual_amount is not None and self.actual_value is None:
                price = PriceList.get_current_price(self.material_type)
                self.actual_value = self.actual_amount * price
        super().save(*args, **kwargs)


class InAppNotification(models.Model):
    """In-app notification for users (bell icon)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.title} ({self.user_id})"


class RequestMaterialLine(models.Model):
    """One material type + weight in a collection request. One request can have multiple lines."""

    class MaterialType(models.TextChoices):
        PAPER = 'paper', 'Бумага'
        CARDBOARD = 'cardboard', 'Картон'
        NEWSPAPERS = 'newspapers', 'Газеты'
        MIXED = 'mixed', 'Смешанная'
        ARCHIVE = 'archive', 'Архивная'

    collection_request = models.ForeignKey(
        CollectionRequest,
        on_delete=models.CASCADE,
        related_name='material_lines',
    )
    material_type = models.CharField(max_length=20, choices=MaterialType.choices)
    amount_kg = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Request Material Line'
        verbose_name_plural = 'Request Material Lines'


class NewsArticle(models.Model):
    """News article for public homepage."""

    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.FileField(upload_to='news_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_articles',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'

    def __str__(self):
        return self.title


class PriceList(models.Model):
    """Material prices (admin-managed). Used for estimated_value and actual_value."""

    class MaterialType(models.TextChoices):
        PAPER = 'paper', 'Бумага'
        CARDBOARD = 'cardboard', 'Картон'
        NEWSPAPERS = 'newspapers', 'Газеты'
        MIXED = 'mixed', 'Смешанная'
        ARCHIVE = 'archive', 'Архивная'

    material_type = models.CharField(max_length=20, choices=MaterialType.choices)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-valid_from']
        verbose_name = 'Price List'
        verbose_name_plural = 'Price Lists'

    def __str__(self):
        return f"{self.get_material_type_display()} — {self.price_per_kg} руб/кг"

    @classmethod
    def get_current_price(cls, material_type):
        from django.utils import timezone
        from decimal import Decimal
        today = timezone.now().date()
        qs = cls.objects.filter(
            material_type=material_type,
            is_active=True,
            valid_from__lte=today,
        ).filter(
            Q(valid_to__isnull=True) | Q(valid_to__gte=today)
        ).order_by('-valid_from')
        row = qs.first()
        return row.price_per_kg if row else Decimal('0')


class RequestWeightLimit(models.Model):
    """Global min/max weight (kg) for collection requests. Single row edited in admin."""

    min_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100,
        help_text='Минимальный суммарный вес заявки (кг)',
    )
    max_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100000,
        help_text='Максимальный суммарный вес заявки (кг)',
    )

    class Meta:
        verbose_name = 'Лимит веса заявок'
        verbose_name_plural = 'Лимиты веса заявок'

    def __str__(self):
        return f'{self.min_kg} – {self.max_kg} кг'

    @classmethod
    def get_limits(cls):
        from decimal import Decimal
        row = cls.objects.first()
        if row:
            return row.min_kg, row.max_kg
        return Decimal('100'), Decimal('100000')
