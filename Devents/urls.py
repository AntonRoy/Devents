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
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import login
from polls.views import *

urlpatterns = [
    path('accounts/room/<int:room_id>/', room),
    path('sign_up/', sign_up),
    path('admin/', admin.site.urls),
    path('accounts/profile/edit_profile/', edit_user),
    path('accounts/profile/', profile),
    path('accounts/member/<int:member_id>/', member),
    path('accounts/edit_room/<int:room_id>/', edit_room),
    path('accounts/edit_event/<int:event_id>/', edit_event),
    path('accounts/event/<int:event_id>/', event),
    path('accounts/task/<int:task_id>/', task),
    path('accounts/sign_up_room/', sign_up_room),
    path('accounts/room/<int:room_id>/add_user', add_user),
    path('login/', login, {'template_name': 'main.html'}, name="main"),
    path('', goto),

    #ajax:
    path('accounts/delete/<int:member_id>/<int:room_id>', delete_user_from_room),
    path('accounts/delete_task/<int:member_id>/<int:task_id>', end_task),
    path('accounts/delete_event/<int:room_id>/<int:event_id>', end_event),
    path('accounts/add_user/<int:user_id>/<int:room_id>', add_one_user),
    path('check_login/<str:login>', check_login),
]