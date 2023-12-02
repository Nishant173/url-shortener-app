import random
import string

from rest_framework.request import Request


def get_client_ip_address(request: Request) -> str:
    x_forwarded_for: str = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR", "")


def get_client_user_agent(request: Request) -> str:
    return request.META.get("HTTP_USER_AGENT", "")


def generate_random_password(*, length: int) -> str:
    assert length > 0, "Param `length` must be > 0"
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return "".join((random.choice(chars) for _ in range(length)))


def generate_random_string(*, length: int) -> str:
    assert length > 0, "Param `length` must be > 0"
    chars = string.ascii_uppercase + string.digits
    return "".join((random.choice(chars) for _ in range(length)))

