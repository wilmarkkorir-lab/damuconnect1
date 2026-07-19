from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.http import JsonResponse


def api_response(status, message, data=None, http_status=200):
    """
    Standard API response format for every endpoint:
    {
        "status": "success" or "error",
        "message": "human readable message",
        "data": {} or null
    }
    """
    return Response(
        {"status": status, "message": message, "data": data},
        status=http_status,
    )


def custom_exception_handler(exc, context):
    # Get default DRF error response
    response = exception_handler(exc, context)

    if response is not None:
        return Response(
            {
                "status": "error",
                "message": _extract_message(response.data),
                "data": None,
            },
            status=response.status_code,
        )
    return response


def _extract_message(data):
    # Flatten DRF error dicts into a single readable string
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                return f"{key}: {value[0]}" if key != "non_field_errors" else str(value[0])
            return str(value)
    if isinstance(data, list):
        return str(data[0])
    return str(data)


def axes_lockout_response(request, credentials, *args, **kwargs):
    # Called by django-axes when an IP is locked out after too many failed logins
    return JsonResponse(
        {
            "status": "error",
            "message": "Too many failed login attempts. Your IP is locked for 30 minutes.",
            "data": None,
        },
        status=429,
    )


class LoginRateThrottle(AnonRateThrottle):
    # Stricter rate limit specifically for the login endpoint — 5 attempts per minute
    scope = 'login'
