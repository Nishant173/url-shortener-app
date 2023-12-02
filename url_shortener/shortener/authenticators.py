from rest_framework import exceptions
from rest_framework.request import Request

from shortener.models import Token


def authenticate_request(request: Request) -> Request:
    """Updates the given `request` object based on the token in the request"""
    token: str = request.headers.get("Authorization", "")
    token = token.strip('Bearer').strip() if token.startswith('Bearer') else ""
    if not token:
        raise exceptions.AuthenticationFailed("Token is missing")
    try:
        instance = Token.objects.get(token=token)
    except Token.DoesNotExist:
        raise exceptions.AuthenticationFailed("Token is invalid")
    request.user = instance.user
    return request

