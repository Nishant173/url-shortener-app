from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import User
from rest_framework import serializers

from shortener.models import ShortUrl, ShortUrlAccessLog

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * 60
SECONDS_PER_YEAR = SECONDS_PER_HOUR * 24 * 365 # Taking 365 days


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, attrs):
        username = attrs["username"]
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"message": f"The given username '{username}' already exists. Please use a different username"})
        return attrs


class ShortUrlCreateSerializer(serializers.Serializer):
    DEFAULT_MAX_USAGE_COUNT = 1

    long_url = serializers.CharField()
    expires_at = serializers.DateTimeField(required=False)
    expires_in_days = serializers.IntegerField(required=False)
    expires_in_hours = serializers.IntegerField(required=False)
    expires_in_minutes = serializers.IntegerField(required=False)
    expires_in_seconds = serializers.IntegerField(required=False)
    max_usage_count = serializers.IntegerField(required=False)

    def validate(self, attrs):
        max_usage_count: int = attrs.get("max_usage_count", ShortUrlCreateSerializer.DEFAULT_MAX_USAGE_COUNT)
        if max_usage_count < 1:
            message = "Expected 'max_usage_count' to be >= 1"
            raise serializers.ValidationError({"message": message})
        has_expires_at = "expires_at" in attrs
        has_expires_in = (
            "expires_in_days" in attrs
            or "expires_in_hours" in attrs
            or "expires_in_minutes" in attrs
            or "expires_in_seconds" in attrs
        )
        if not has_expires_at and not has_expires_in:
            message = (
                "Expected either 'expires_at' or any of 'expires_in_days', 'expires_in_hours', 'expires_in_minutes', 'expires_in_seconds'"
            )
            raise serializers.ValidationError({"message": message})
        if has_expires_at and has_expires_in:
            message = (
                "Expected either 'expires_at' or any of 'expires_in_days', 'expires_in_hours', 'expires_in_minutes', 'expires_in_seconds'; but not both"
            )
            raise serializers.ValidationError({"message": message})
        dt_now = datetime.now().astimezone(timezone.utc)
        if has_expires_at:
            computed_expires_at: datetime = attrs["expires_at"].astimezone(timezone.utc)
        elif has_expires_in:
            computed_expires_at: datetime = (
                dt_now
                + timedelta(
                    days=attrs.get("expires_in_days", 0),
                    hours=attrs.get("expires_in_hours", 0),
                    minutes=attrs.get("expires_in_minutes", 0),
                    seconds=attrs.get("expires_in_seconds", 0),
                )
            ).astimezone(timezone.utc)
        is_valid_expiry: bool = (
            computed_expires_at > dt_now
            # and SECONDS_PER_HOUR <= (computed_expires_at - dt_now).total_seconds() <= SECONDS_PER_YEAR
            and SECONDS_PER_MINUTE <= (computed_expires_at - dt_now).total_seconds() <= SECONDS_PER_YEAR
        )
        if not is_valid_expiry:
            message = "The given expiry datetime is out of bounds. Expected expiry time to be between 1 minute and 1 year"
            raise serializers.ValidationError({"message": message})
        attrs["computed_expires_at"] = computed_expires_at
        return {
            "computed_expires_at": computed_expires_at,
            "long_url": attrs["long_url"],
            "max_usage_count": max_usage_count,
        }


class ShortUrlReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortUrl
        fields = [
            "id",
            "created_at",
            "updated_at",
            "user_id",
            "short_url",
            "long_url",
            "usage_count",
            "max_usage_count",
            "expires_at",
        ]

    def to_representation(self, instance):
        return super().to_representation(instance)


class ShortUrlAccessLogReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortUrlAccessLog
        fields = [
            "id",
            "created_at",
            "updated_at",
            "short_url",
            "ip_address",
            "user_agent",
            "timestamp",
        ]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
            "short_url_id": instance.short_url_id,
            "short_url_data": self.context.get("short_url_data_dict", {}).get(instance.short_url_id, None),
            "ip_address": instance.ip_address,
            "user_agent": instance.user_agent,
            "timestamp": instance.timestamp,
        }

