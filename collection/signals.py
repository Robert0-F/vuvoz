"""
Signals for email and in-app notifications.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver, Signal

from .models import BonusConfig, CollectionRequest, InstitutionBonus, InAppNotification, InstitutionProfile, SupportConfig
from .services.email_service import send_platform_email

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
    send_platform_email(subject=subject, message=body, recipient_list=[email])


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
    send_platform_email(subject=subject, message=body, recipient_list=[to_email])
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
    status_labels = {
        'accepted': 'Принята',
        'pending_confirmation': 'Ожидает подтверждения вывоза',
        'completed': 'Завершена',
    }
    status_display = status_labels.get(instance.status, instance.status)
    subject = f"Заявка {num} — обновление статуса"
    extra = ''
    if instance.status == CollectionRequest.Status.ACCEPTED and instance.actual_collection_date:
        extra = f"\nДата вывоза (назначена компанией): {instance.actual_collection_date}\n"
    if instance.status == CollectionRequest.Status.PENDING_CONFIRMATION:
        extra = (
            f"\nКомпания указала фактический вес: {instance.actual_amount} кг."
            f"\nПодтвердите, что вывоз выполнен с этим весом.\n"
        )
    body = (
        f"Здравствуйте,\n\n"
        f"Статус вашей заявки {num} изменён.\n\n"
        f"Новый статус: {status_display}\n"
        f"Вес заявки: {instance.paper_weight_kg} кг{extra}\n"
        f"С уважением,\nСервис вывоза макулатуры"
    )
    send_platform_email(subject=subject, message=body, recipient_list=[to_email])
    notif_msg = f"Заявка {num}: {status_display}."
    if instance.status == CollectionRequest.Status.PENDING_CONFIRMATION:
        notif_msg = f"Заявка {num}: подтвердите фактический вес {instance.actual_amount} кг."
    InAppNotification.objects.create(
        user=inst_user,
        title="Обновление статуса заявки",
        message=notif_msg,
        link="/institution",
    )


def _create_bonus_if_completed(instance):
    """Create a pending InstitutionBonus when request is completed (if not already created)."""
    if instance.status != CollectionRequest.Status.COMPLETED:
        return
    if hasattr(instance, 'institution_bonus') and instance.institution_bonus:
        return
    percent = BonusConfig.get_percent()
    if percent <= 0:
        return
    order_value = instance.actual_value or instance.estimated_value or 0
    if order_value <= 0:
        return
    from decimal import Decimal
    calculated = (order_value * percent / Decimal('100')).quantize(Decimal('0.01'))
    InstitutionBonus.objects.get_or_create(
        collection_request=instance,
        defaults={
            'institution': instance.institution,
            'calculated_amount': calculated,
            'awarded_amount': calculated,
            'status': InstitutionBonus.Status.PENDING,
        },
    )


@receiver(post_save, sender=CollectionRequest)
def on_collection_request_save(sender, instance, created, **kwargs):
    """New request: notify company. Status change: notify institution. Completed: create pending bonus."""
    if created:
        _notify_company_new_request(instance)
        _create_bonus_if_completed(instance)
        return
    previous = getattr(instance, '_previous_status', None)
    if previous != instance.status and instance.status in (
        'accepted', 'pending_confirmation', 'completed',
    ):
        _notify_institution_status_change(instance, previous)
    if instance.status == CollectionRequest.Status.COMPLETED:
        _create_bonus_if_completed(instance)


@receiver(post_save, sender=InstitutionProfile)
def assign_support_user_to_new_institution(sender, instance, created, **kwargs):
    """New institutions automatically get the global support specialist."""
    if not created or instance.support_user_id:
        return
    support_user = SupportConfig.get_support_user()
    if support_user:
        InstitutionProfile.objects.filter(pk=instance.pk).update(support_user=support_user)