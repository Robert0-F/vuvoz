from rest_framework.throttling import AnonRateThrottle


class PublicFormThrottle(AnonRateThrottle):
    """Rate limit for public registration and pickup forms."""

    scope = 'public_form'
