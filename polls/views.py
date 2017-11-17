from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
import code

from .models import Room, Event, Person

def main(request):
    if request.method == 'POST':
        login = request.POST['login']
        password = request.POST['password']
        user = authenticate(username=login, password=password)
        if user is not None:
            return redirect("profile")
        else:
            return render(request, 'main.html', {'error': "Неверный пароль или логин!"})
    return render(request, 'main.html', {'error': " "})

def sign_up(request):
    if request.method == 'POST':
        name = request.POST['name']
        lastname = request.POST['lastname']
        login = request.POST['login']
        vk_id = request.POST['VK']
        password = request.POST['password']
        repassword = request.POST['repassword']
        if password == repassword:
            try:
                user = User.objects.create_user(username=login, password=password, email=login, first_name=name,
                                                last_name=lastname)
                Person.objects.get_or_create(user=user, vk_id=vk_id)
                return redirect("main")
            except:
                return render(request, 'sign_up.html', {'error': 'Cуществует пользователь с таким же логином'})
        else:
            return render (request, 'sign_up.html', {'error': 'Пароли не совпадают'})
    return render (request, 'sign_up.html', {'error': ' '})

def profile(request):
    return render(request, 'profile.html',
                  {'name': request.user.first_name, 'lastname': request.user.last_name,
                   'events': list(request.user.person.events.all()), 'groups': list(request.user.person.agroups.all()) + list(request.user.person.ugroups.all())})


def room(request, room_id):
    if request.method == 'GET':
        # data =
        return render(request, "room.htl", {''})
    return render(request, "room.html", {'members': list(room.users.all()) + list(room.admins.all()), 'events': room.events})
