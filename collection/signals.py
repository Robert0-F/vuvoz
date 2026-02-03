"""
Signals for email notifications (institution created, request status changed).
Uses Django's email backend (console in dev, SMTP in production).
"""
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal
from django.conf import settings

from .models import CollectionRequest, InstitutionProfile

# Custom signal: institution created with credentials (sent from serializer)
institution_created = Signal()


@receiver(institution_created)
def send_institution_credentials(sender, instance, password, email, **kwargs):
    """Send credentials email when a new institution account is created."""
    subject = "Your institution account - Waste Paper Collection"
    body = (
        f"Hello,\n\n"
        f"An account has been created for your institution.\n\n"
        f"Username: {email}\n"
        f"Password: {password}\n\n"
        f"Please sign in and change your password after first login.\n\n"
        f"Best regards,\nWaste Paper Collection"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )


@receiver(pre_save, sender=CollectionRequest)
def store_previous_request_status(sender, instance, **kwargs):
    """Store previous status so we can detect changes in post_save."""
    if instance.pk:
        try:
            instance._previous_status = CollectionRequest.objects.get(pk=instance.pk).status
        except CollectionRequest.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=CollectionRequest)
def send_request_status_change_email(sender, instance, created, **kwargs):
    """Notify institution when request status changes (accepted/completed)."""
    if created:
        return
    previous = getattr(instance, '_previous_status', None)
    if previous == instance.status:
        return
    if instance.status not in ('accepted', 'completed'):
        return
    to_email = instance.institution.email
    subject = f"Collection request #{instance.pk} - status updated"
    body = (
        f"Hello,\n\n"
        f"Your collection request #{instance.pk} has been updated.\n\n"
        f"New status: {instance.status}\n"
        f"Weight: {instance.paper_weight_kg} kg\n\n"
        f"Best regards,\nWaste Paper Collection"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=True,
    )
