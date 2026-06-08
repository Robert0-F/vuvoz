import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from django.conf import settings

from collection.models import AuditLog


MAX_PAYLOAD_LEN = 4000


def _safe_value(value: Any):
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def _mask_sensitive(data: dict[str, Any]) -> dict[str, Any]:
    masked = {}
    for k, v in data.items():
        key = k.lower()
        if any(s in key for s in ("password", "token", "secret")):
            masked[k] = "***"
        else:
            masked[k] = _safe_value(v)
    return masked


def _request_meta(request):
    if not request:
        return "", ""
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:255]
    return ip, user_agent


def write_audit_log(
    *,
    request=None,
    actor=None,
    action_type: str,
    short_summary: str,
    category: str = AuditLog.Category.INFO,
    target_model: str = "",
    target_id: Any = "",
    payload: dict[str, Any] | None = None,
):
    payload = payload or {}
    payload = _mask_sensitive(payload)
    try:
        payload_str = json.dumps(payload, ensure_ascii=False, default=str)
        if len(payload_str) > MAX_PAYLOAD_LEN:
            payload = {"truncated": True, "note": f"payload>{MAX_PAYLOAD_LEN} chars"}
    except Exception:
        payload = {"error": "payload_serialization_failed"}

    if actor is None and request is not None and getattr(request, "user", None) and request.user.is_authenticated:
        actor = request.user
    actor_role = getattr(actor, "role", "") if actor else ""
    ip, user_agent = _request_meta(request)

    AuditLog.objects.create(
        actor=actor if getattr(actor, "pk", None) else None,
        actor_role=actor_role or "",
        action_type=action_type,
        category=category,
        target_model=target_model[:120],
        target_id=str(target_id)[:64] if target_id is not None else "",
        short_summary=short_summary[:255],
        payload_json=payload,
        ip_address=ip[:64],
        user_agent=user_agent,
    )


def cleanup_old_audit_logs():
    days = int(getattr(settings, "AUDIT_LOG_RETENTION_DAYS", 180))
    if days <= 0:
        return 0
    from django.utils import timezone

    threshold = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = AuditLog.objects.filter(created_at__lt=threshold).delete()
    return deleted

