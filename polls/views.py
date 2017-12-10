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
                  {'ID': request.user.person.id ,'name': request.user.first_name, 'lastname': request.user.last_name,
                   'events': list(request.user.person.events.all()), 'groups': list(request.user.person.agroups.all()) + list(request.user.person.ugroups.all())})


def sign_up_room(request):
    if request.method == 'POST':
        # data = request.POST
        #code.interact(local=locals())
        name = request.POST['room_name']
        cmt = request.POST['discription']

        # user_ids = request.POST['members']
        # users = []
        # for id in user_ids:
        #     user = User.objects(id=id)
        #     if user:
        #         users += user
        admin=request.user.person
        Room.objects.get_or_create(name=name, cmt=cmt)
        room = Room.objects.get(name=name)
        # code.interact(local=locals())
        room.admins=[admin]
        return redirect('/accounts/profile')
    return render(request, 'sign_up_room.html')

def room(request, room_id):
    if request.method == "GET":
        #code.interact(local=locals())
        room = Room.objects.get(id=room_id)
        admin = 1
        # if request.user.id in room.admins:
        #     admin=1
        return render(request, "room.html", {'error': "",'room_id': room_id, 'room_name': room.name,
                                             'members': list(room.users.all()) + list(room.admins.all()),
                                             'events': list(room.events.all())})
    if request.method=="POST":
        id_ = request.POST["id_"]
        room = Room.objects.get(id=room_id)
        admin = 1
        try:
            user = Person.objects.get(id=id_)
            users = list(room.users.all()) + [user]
            room.users = users
            room.save()
            return render(request, "room.html", {'error': "", 'room_id': room_id, 'room_name': room.name,
                                                 'members': list(room.users.all()) + list(room.admins.all()),
                                                 'events': list(room.events.all())})
        except:
            return render(request, "room.html", {'error': "This user doesn't exist", 'room_id': room_id, 'room_name': room.name,
                                                 'members': list(room.users.all()) + list(room.admins.all()),
                                                 'events': list(room.events.all())})



def sign_up_event(request, room_id):
    if request.method == 'POST':
        name = request.POST['event_name']
        cmt = request.POST['discription']
        # date = str(request.POST['data']+' '+request.POST['time'])
        day = request.POST['data'].split()
        # sorry za govnokod, tak nado
        if int(day[0])<10:
            day[0]='0'+day[0]
        months = ['January,', 'February,', 'March,', 'April,', 'May,', 'June,', 'Jule,', 'August,', 'September,', 'October,', 'November,', 'December,']
        for i in range(12):
            if day[1]==months[i]:
                day[1]=str(i+1)
                if int(day[1])<10:
                    day[1]='0'+day[1]
        date = str(day[2]+'-'+day[1]+'-'+day[0]+' '+request.POST['time'])


        Event.objects.get_or_create(name=name, cmt=cmt, date=date, room=Room.objects.get(id=room_id))
        return redirect("/accounts/room/{0}".format(room_id))
    return render(request, 'sign_up_event.html')

def event(request, event_id):
    if request.method == "GET":
        event = Event.objects.get(id=event_id)
        admin = 1
        return render(request, 'event.html', {'admin': admin, 'event_name': event.name, 'members': list(event.users.all()), 'time': event.date, 'discription': event.cmt})