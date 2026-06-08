import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_platform_email(subject: str, message: str, recipient_list: list[str]) -> bool:
    """Send email and log delivery errors instead of silencing them."""
    if not recipient_list:
        return False
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Failed to send email. subject=%s recipients=%s", subject, recipient_list)
        return False

