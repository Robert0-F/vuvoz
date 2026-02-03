from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """User model with role: Collection Company or Institution."""

    class Role(models.TextChoices):
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
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    paper_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    desired_date = models.DateField(null=True, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Collection Request'
        verbose_name_plural = 'Collection Requests'

    def __str__(self):
        return f"Request #{self.pk} - {self.institution.institution_name} ({self.paper_weight_kg} kg)"

    def save(self, *args, **kwargs):
        # Auto-set receiving_company from institution's parent_company
        if self.institution_id and not self.receiving_company_id:
            self.receiving_company = self.institution.parent_company
        super().save(*args, **kwargs)
