from django.urls import path

from shortener.views import HomeView, ShortUrlView, ShortUrlAccessLogView, UserView


urlpatterns = [
    path("", HomeView.as_view({"get": "get"})),
    path("users/", UserView.as_view({"post": "create_one"})),
    path("short-urls/", ShortUrlView.as_view({"get": "get_all", "post": "create_one"})),
    path("short-urls/<str:short_url>", ShortUrlView.as_view({"get": "get_one"})),
    path("short-urls/<str:short_url>/redirect", ShortUrlView.as_view({"get": "get_one_redirect"})),
    path("short-urls-log/", ShortUrlAccessLogView.as_view({"get": "get_all"})),
]
