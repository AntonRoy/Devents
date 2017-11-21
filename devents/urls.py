"""Devents URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login
from polls.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^main/', login, {'template_name': 'main.html'}, name="main"),
    url(r'^sign_up/', sign_up, name="sign_up"),
    url(r'^accounts/profile/(?P<room_id>[0-9]{1})', room, name='room'),
    url(r'^accounts/profile/sign_up_room', sign_up_room, name='sign_up_room'),
    url(r'^accounts/profile/', profile, name="profile"),

]
