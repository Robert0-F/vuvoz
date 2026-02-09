"""
Shared validators for institution and request forms.
"""
import re
from decimal import Decimal

from rest_framework import serializers

# Russian phone: +7 followed by 10 digits (spaces optional)
PHONE_RU_PATTERN = re.compile(r'^\+7[\s\d]{10,12}$')

PAPER_WEIGHT_MIN = Decimal('1')
PAPER_WEIGHT_MAX = Decimal('10000')


def validate_email_format(value: str) -> str:
    """Validate email format (basic)."""
    if not value or not value.strip():
        raise serializers.ValidationError('Введите адрес почты.')
    value = value.strip().lower()
    if '@' not in value or '.' not in value.split('@')[-1]:
        raise serializers.ValidationError('Некорректный формат почты.')
    return value


def validate_phone_ru(value: str) -> str:
    """Validate Russian phone format: +7 XXX XXX XX XX."""
    if not value or not value.strip():
        raise serializers.ValidationError('Введите номер телефона.')
    cleaned = re.sub(r'\s', '', value.strip())
    if not (cleaned.startswith('+7') and len(cleaned) == 12 and cleaned[1:].isdigit()):
        raise serializers.ValidationError('Формат: +7 XXX XXX XX XX')
    return value.strip()


def validate_paper_weight_kg(value) -> Decimal:
    """Validate paper weight between 1 and 10000 kg."""
    try:
        weight = Decimal(str(value))
    except Exception:
        raise serializers.ValidationError('Укажите число (кг).')
    if weight < PAPER_WEIGHT_MIN:
        raise serializers.ValidationError(f'Минимум {PAPER_WEIGHT_MIN} кг.')
    if weight > PAPER_WEIGHT_MAX:
        raise serializers.ValidationError(f'Максимум {PAPER_WEIGHT_MAX} кг.')
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
