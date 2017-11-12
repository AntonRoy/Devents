from django.shortcuts import render
from django.http import HttpResponse
import code

from .models import Room, Event, User

def main(request):
    if request.method == 'POST':
        login = request.POST['login']
        password = request.POST['password']
        true_password = User(login=login).password
        if password == true_password:
            data = User(login=login)
            return render(request, 'profile.html', {'name':data.name, 'lastname':data.last_name, 'events':data.events, 'groups':data.groups})
        else:
            return render(request, 'main.html', {'error':" Неверный пароль или логин!"})

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
                data = User.objects.get(login=login)
                return render(request, 'sign_up.html', {'error': 'Cуществует пользователь с таким же логином'})
            except:
                User.objects.get_or_create(name=name, last_name=lastname, login=login, password=password, vk_id=vk_id)
                data = User.objects.get(login=login)
                return render(request, 'profile.html', {'name':data.name, 'lastname':data.last_name, 'events':[], 'groups':[]})
        else:
            return render (request, 'sign_up.html', {'error': 'Пароли не совпадают'})
    return render (request, 'sign_up.html', {'error': ' '})


# Create your views here.
