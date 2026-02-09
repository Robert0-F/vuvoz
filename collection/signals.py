"""
Signals for email and in-app notifications.
"""
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal
from django.conf import settings

from .models import CollectionRequest, InAppNotification, InstitutionProfile

# Custom signal: institution created with credentials (sent from serializer)
institution_created = Signal()


@receiver(institution_created)
def send_institution_credentials(sender, instance, password, email, **kwargs):
    """Send credentials email when a new institution account is created."""
    subject = "Ваш аккаунт организации - Вывоз макулатуры"
    body = (
        f"Здравствуйте,\n\n"
        f"Для вашей организации создан аккаунт.\n\n"
        f"Логин: {email}\n"
        f"Пароль: {password}\n\n"
        f"Пожалуйста, смените пароль после первого входа.\n\n"
        f"С уважением,\nСервис вывоза макулатуры"
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


def _notify_company_new_request(instance):
    """Email + in-app notification to company when new request is created."""
    company_user = instance.receiving_company.user
    to_email = instance.receiving_company.contact_email
    num = instance.request_number or str(instance.pk)
    subject = f"Новый запрос на вывоз макулатуры {num}"
    body = (
        f"Поступил новый запрос на вывоз макулатуры.\n\n"
        f"Номер: {num}\n"
        f"Организация: {instance.institution.institution_name}\n"
        f"Вес: {instance.paper_weight_kg} кг\n"
        f"Срочность: {instance.get_urgency_display()}\n\n"
        f"С уважением,\nСервис вывоза макулатуры"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=True,
    )
    InAppNotification.objects.create(
        user=company_user,
        title="Новый запрос на вывоз",
        message=f"Заявка {num} от {instance.institution.institution_name} ({instance.paper_weight_kg} кг).",
        link=f"/company",
    )


def _notify_institution_status_change(instance, previous_status):
    """Email + in-app notification to institution when status changes."""
    to_email = instance.institution.email
    inst_user = instance.institution.user
    num = instance.request_number or str(instance.pk)
    status_display = dict(CollectionRequest.Status.choices).get(instance.status, instance.status)
    subject = f"Заявка {num} — обновление статуса"
    body = (
        f"Здравствуйте,\n\n"
        f"Статус вашей заявки {num} изменён.\n\n"
        f"Новый статус: {status_display}\n"
        f"Вес: {instance.paper_weight_kg} кг\n\n"
        f"С уважением,\nСервис вывоза макулатуры"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=True,
    )
    InAppNotification.objects.create(
        user=inst_user,
        title="Обновление статуса заявки",
        message=f"Заявка {num}: {status_display}.",
        link="/institution",
    )


@receiver(post_save, sender=CollectionRequest)
def on_collection_request_save(sender, instance, created, **kwargs):
    """New request: notify company. Status change: notify institution."""
    if created:
        _notify_company_new_request(instance)
        return
    previous = getattr(instance, '_previous_status', None)
    if previous == instance.status:
        return
    if instance.status in ('accepted', 'completed'):
        _notify_institution_status_change(instance, previous)
