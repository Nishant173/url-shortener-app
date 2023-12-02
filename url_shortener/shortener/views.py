from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from rest_framework import status, viewsets
# from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from shortener.authenticators import authenticate_request
from shortener.models import ShortUrl, ShortUrlAccessLog, Token
from shortener.serializers import (
    ShortUrlAccessLogReadOnlySerializer,
    ShortUrlCreateSerializer,
    ShortUrlReadOnlySerializer,
    UserCreateSerializer,
)
from shortener import utils


class HomeView(viewsets.ViewSet):

    def get(self, request: Request):
        return Response(data={"message": "Welcome to the URL shortner application's base URL"}, status=status.HTTP_200_OK)


class UserView(viewsets.ViewSet):

    def create_one(self, request: Request):
        ser = UserCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        username = ser.validated_data["username"]
        user = User.objects.create(
            username=username,
            password=utils.generate_random_password(length=16),
            last_login=datetime.utcnow(),
        )
        response_data = {
            "user_id": user.id,
            "username": user.username,
            "token": Token.create_unique_token_for_user(user=user),
        }
        return Response(data=response_data, status=status.HTTP_201_CREATED)


class ShortUrlView(viewsets.ViewSet):

    def log_access_of_short_url(self, *, short_url: ShortUrl, request: Request):
        """Logs the IP address, user agent of the given request"""
        return ShortUrlAccessLog.objects.create(
            short_url=short_url,
            ip_address=utils.get_client_ip_address(request),
            user_agent=utils.get_client_user_agent(request),
            timestamp=datetime.utcnow(),
        )

    def get_all(self, request: Request):
        request = authenticate_request(request=request)
        queryset = ShortUrl.objects.filter(user_id=request.user.id).order_by("-created_at")
        response_data = ShortUrlReadOnlySerializer(instance=queryset, many=True).data
        return Response(data=response_data, status=status.HTTP_200_OK)

    def get_one(self, request: Request, short_url: str):
        try:
            instance = ShortUrl.objects.get(
                short_url=short_url,
            )
        except ShortUrl.DoesNotExist:
            return Response(data={"message": f"The given short URL '{short_url}' is not found"}, status=status.HTTP_404_NOT_FOUND)
        if instance.has_expired():
            return Response(data={"message": f"The given short URL '{short_url}' has expired"}, status=status.HTTP_404_NOT_FOUND)
        if instance.has_reached_max_usage_limit():
            return Response(data={"message": f"The given short URL '{short_url}' has reached max usage limit"}, status=status.HTTP_404_NOT_FOUND)
        instance.usage_count += 1
        instance.save()
        self.log_access_of_short_url(short_url=instance, request=request)
        response_data = ShortUrlReadOnlySerializer(instance=instance).data
        return Response(data=response_data, status=status.HTTP_200_OK)

    def get_one_redirect(self, request: Request, short_url: str):
        try:
            instance = ShortUrl.objects.get(
                short_url=short_url,
            )
        except ShortUrl.DoesNotExist:
            return Response(data={"message": f"The given short URL '{short_url}' is not found"}, status=status.HTTP_404_NOT_FOUND)
        if instance.has_expired():
            return Response(data={"message": f"The given short URL '{short_url}' has expired"}, status=status.HTTP_404_NOT_FOUND)
        if instance.has_reached_max_usage_limit():
            return Response(data={"message": f"The given short URL '{short_url}' has reached max usage limit"}, status=status.HTTP_404_NOT_FOUND)
        instance.usage_count += 1
        instance.save()
        self.log_access_of_short_url(short_url=instance, request=request)
        return HttpResponseRedirect(redirect_to=instance.long_url)

    def create_one(self, request: Request):
        request = authenticate_request(request=request)
        serializer = ShortUrlCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = ShortUrl.objects.create(
            user_id=request.user.id,
            short_url=ShortUrl.compute_short_url(long_url=serializer.validated_data["long_url"]),
            long_url=serializer.validated_data["long_url"],
            usage_count=0,
            max_usage_count=serializer.validated_data["max_usage_count"],
            expires_at=serializer.validated_data["computed_expires_at"],
        )
        response_data = ShortUrlReadOnlySerializer(instance=instance).data
        return Response(data=response_data, status=status.HTTP_201_CREATED)


class ShortUrlAccessLogView(viewsets.ViewSet):

    def get_all(self, request: Request):
        queryset = ShortUrlAccessLog.objects.filter().order_by("-created_at")
        short_url_data_list = list(
            ShortUrl.objects.filter(
                id__in=list(queryset.values_list("short_url_id", flat=True)),
            ).values("id", "short_url", "long_url", "expires_at")
        )
        short_url_data_dict = { item["id"] : item for item in short_url_data_list }
        response_data = ShortUrlAccessLogReadOnlySerializer(
            instance=queryset,
            many=True,
            context={"short_url_data_dict": short_url_data_dict},
        ).data
        return Response(data=response_data, status=status.HTTP_200_OK)

