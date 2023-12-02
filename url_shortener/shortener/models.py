from datetime import datetime, timezone
import random
import string
import uuid

from django.contrib.auth.models import User
from django.db import models
from rest_framework.request import Request

from shortener.utils import generate_random_string

SHORT_URL_CHARSET = string.ascii_lowercase


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        abstract = True

    def as_dict(self):
        return


class Token(BaseModel):
    token = models.CharField(max_length=100, db_index=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    @staticmethod
    def create_unique_token_for_user(*, user: User) -> str:
        token = generate_random_string(length=20)
        instance = Token.objects.create(token=token, user=user)
        return instance.token


class ShortUrl(BaseModel):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, db_index=True)
    short_url = models.CharField(max_length=100, db_index=True, unique=True)
    long_url = models.CharField(max_length=500)
    usage_count = models.PositiveIntegerField(default=0)
    max_usage_count = models.PositiveIntegerField()
    expires_at = models.DateTimeField()

    @staticmethod
    def compute_short_url(long_url: str) -> str:
        return "".join((random.choice(SHORT_URL_CHARSET) for _ in range(8))) + ".abc"

    def has_expired(self) -> bool:
        return datetime.now().astimezone(timezone.utc) > self.expires_at.astimezone(timezone.utc)

    def has_reached_max_usage_limit(self) -> bool:
        return self.usage_count >= self.max_usage_count


class ShortUrlAccessLog(BaseModel):
    short_url = models.ForeignKey(to=ShortUrl, on_delete=models.CASCADE, db_index=True)
    ip_address = models.CharField(max_length=1000)
    user_agent = models.CharField(max_length=1000)
    timestamp = models.DateTimeField()
