"""
Shared validators for institution and request forms.
"""
import re
from decimal import Decimal

from rest_framework import serializers

# Russian phone: +7 or 7 followed by 10 digits (spaces optional)
PHONE_RU_PATTERN = re.compile(r'^\+?7[\s\d]{10,12}$')

def _get_request_weight_limits():
    from collection.models import RequestWeightLimit
    return RequestWeightLimit.get_limits()


def validate_email_format(value: str) -> str:
    """Validate email format (basic)."""
    if not value or not value.strip():
        raise serializers.ValidationError('Введите адрес почты.')
    value = value.strip().lower()
    if '@' not in value or '.' not in value.split('@')[-1]:
        raise serializers.ValidationError('Некорректный формат почты.')
    return value


def validate_phone_ru(value: str) -> str:
    """Validate Russian phone format: 7 XXX XXX XX XX or +7 XXX XXX XX XX (плюс необязателен)."""
    if not value or not value.strip():
        raise serializers.ValidationError('Введите номер телефона.')
    cleaned = re.sub(r'\s', '', value.strip())
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    if cleaned.startswith('8') and len(cleaned) == 11:
        cleaned = '7' + cleaned[1:]
    if not (cleaned.startswith('7') and len(cleaned) == 11 and cleaned.isdigit()):
        raise serializers.ValidationError('Формат: 7 XXX XXX XX XX или +7 XXX XXX XX XX (10 цифр после 7).')
    return '+7 ' + re.sub(r'(\d{3})(\d{3})(\d{2})(\d{2})', r'\1 \2 \3 \4', cleaned[1:])


def validate_paper_weight_kg(value, use_total_min=False) -> Decimal:
    """Validate paper weight. Per-line: min 1 kg, max from admin. For total sum use use_total_min=True."""
    min_kg, max_kg = _get_request_weight_limits()
    try:
        weight = Decimal(str(value))
    except Exception:
        raise serializers.ValidationError('Укажите число (кг).')
    effective_min = min_kg if use_total_min else Decimal('1')
    if weight < effective_min:
        raise serializers.ValidationError(f'Минимум {effective_min} кг.')
    if weight > max_kg:
        raise serializers.ValidationError(f'Максимум {max_kg} кг.')
    return weight


def validate_inn(value: str) -> str:
    """ИНН: 10 цифр (юрлицо) или 12 цифр (физлицо/ИП)."""
    if not value:
        return ''
    cleaned = re.sub(r'\s', '', str(value).strip())
    if not cleaned.isdigit():
        raise serializers.ValidationError('ИНН должен содержать только цифры.')
    if len(cleaned) not in (10, 12):
        raise serializers.ValidationError('ИНН: 10 цифр (юрлицо) или 12 цифр (ИП).')
    return cleaned


def validate_kpp(value: str) -> str:
    """КПП: 9 цифр."""
    if not value:
        return ''
    cleaned = re.sub(r'\s', '', str(value).strip())
    if not cleaned.isdigit():
        raise serializers.ValidationError('КПП должен содержать только цифры.')
    if len(cleaned) != 9:
        raise serializers.ValidationError('КПП должен содержать 9 цифр.')
    return cleaned


def validate_ogrn(value: str) -> str:
    """ОГРН: 13 цифр (юрлицо) или 15 цифр (ОГРНИП)."""
    if not value:
        return ''
    cleaned = re.sub(r'\s', '', str(value).strip())
    if not cleaned.isdigit():
        raise serializers.ValidationError('ОГРН должен содержать только цифры.')
    if len(cleaned) not in (13, 15):
        raise serializers.ValidationError('ОГРН: 13 цифр (юрлицо) или 15 цифр (ОГРНИП).')
    return cleaned
