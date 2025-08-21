"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from pages.views import home_view, url_view, download_url, api_search_video, api_search_playlist, api_download_thumbnail, api_download_video, api_playlist_items
from django.urls import include, path

urlpatterns = [
    path('', home_view, name='home'),
    path('home', home_view, name='home'),
    path('service.html', home_view, name='home'),
    path('index.html', home_view, name='home'),
    path('about.html', home_view, name='home'),
    path('contact.html', home_view, name='home'),
    path('post/url', url_view, name = "post_url"),
    path('download/url', download_url, name = "download_url"),
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    path('api/search-video/', api_search_video, name='api_search_video'),
    path('api/search-playlist/', api_search_playlist, name='api_search_playlist'),
    path('api/download-thumbnail/', api_download_thumbnail, name='api_download_thumbnail'),
    path('api/download-video/', api_download_video, name='api_download_video'),
    path('api/playlist-items/', api_playlist_items, name='api_playlist_items'),
]