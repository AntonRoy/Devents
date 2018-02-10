from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from vkplus import *
import vk_settings
import code
from datetime import *

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
                return redirect("/login/")
            except:
                return render(request, 'sign_up.html', {'error': 'Cуществует пользователь с таким же логином'})
        else:
            return render (request, 'sign_up.html', {'error': 'Пароли не совпадают'})
    return render (request, 'sign_up.html', {'error': ' '})


def profile(request):
    user=request.user
    events_and_tasks = list(request.user.person.events.all())
    tasks = []
    events = []
    for et in events_and_tasks:
        if et.is_task:
            tasks.append(et)
        else:
            events.append(et)
    return render(request, 'profile.html',
                  {'user': user,
                   'events': events,
                   'tasks': tasks,
                   'groups': list(user.person.agroups.all()) + list(user.person.ugroups.all())})


def edit_user(request):
    name = request.user.username
    user = User.objects.get(username=name)
    if request.method=="POST":
        user.first_name = request.POST['name']
        user.last_name = request.POST['lastname']
        if request.POST['password'] != '' and request.POST['repassword'] != '':
            if request.POST['password']==request.POST['repassword']:
                user.set_password(request.POST['password'])
            else:
                return render(request, 'edit_user.html', {'error': 'Пароли не совпадают'})
        user.save()
        return redirect('/login')
    user = request.user
    return render(request, 'edit_user.html')


def sign_up_room(request):
    if request.method == 'POST':
        name = request.POST['room_name']
        cmt = request.POST['discription']
        admin = request.user.person
        Room.objects.get_or_create(name=name, cmt=cmt)
        room = Room.objects.get(name=name)
        room.admins.set([admin])
        return redirect('/accounts/profile')
    return render(request, 'sign_up_room.html')


def room(request, room_id):
    if request.method == "GET":
        admin = 0
        room = Room.objects.get(id=room_id)
        if request.user.person in room.admins.all():
            admin = 1
        if admin:
            pre_events = list(room.events.filter(is_task=0))
            events = []
            for event in pre_events:
                if list(event.users.all()):
                    events.append(event)
            pre_tasks = list(room.events.filter(is_task=1))
            tasks = []
            for task in pre_tasks:
                if list(task.users.all()):
                    tasks.append(task)
        else:
            events = []
            tasks = []
            for event in list(room.events.all()):
                if request.user.person in event.users.all():
                    if event.is_task == 0:
                        events.append(event)
                    else:
                        tasks.append(event)
        users_tasks = []
        users = list(room.users.all()) + list(room.admins.all())
        for user in users:
            user_tasks = []
            for event in list(room.events.filter(is_task=1)):
                if user in event.users.all():
                    user_tasks.append(event)
            users_tasks.append(user_tasks)
            data = list(zip(users_tasks, users))
        for event in events:
            if event.date.month:
                a = 1
        return render(request, "room.html", {'error': "",
                                             'data': data,
                                             'room': room,
                                             'members': list(room.users.all()),
                                             'admins': list(room.admins.all()),
                                             'admin': admin,
                                             'events': events,
                                             'tasks': tasks,
                                             'discription': room.cmt,
                                             })
    if request.method=="POST":
        room = Room.objects.get(id=room_id)
        id_ = request.POST["id_"]
        users = list(room.users.all())
        er = ""
        try:
            user = Person.objects.get(id=id_)
            if user not in users:
                room.users.set(list(room.users.all()) + [user])
        except:
            er = "Такого пользоватателя не существует"
        admin = 0
        room = Room.objects.get(id=room_id)
        if request.user.person in room.admins.all():
            admin = 1
        if admin:
            events = list(room.events.filter(is_task=0))
            tasks = list(room.events.filter(is_task=1))
        else:
            events = []
            tasks = []
            for event in list(room.events.all()):
                if request.user.person in event.users.all():
                    if event.is_task == 0:
                        events.append(event)
                    else:
                        tasks.append(event)
        users_tasks = []
        users = list(room.users.all()) + list(room.admins.all())
        for user in users:
            user_tasks = []
            for event in list(room.events.filter(is_task=1)):
                if user in event.users.all():
                    user_tasks.append(event)
            users_tasks.append(user_tasks)
            data = list(zip(users_tasks, users))
        return render(request, "room.html", {'error': er,
                                      'data': data,
                                      'room': room,
                                      'members': list(room.users.all()),
                                      'admins': list(room.admins.all()),
                                      'admin': admin,
                                      'events': events,
                                      'tasks': tasks,
                                      'discription': room.cmt,
                                      })


def edit_room(request, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == 'POST':
        room.name = request.POST['room_name']
        room.cmt = request.POST['discription']
        room.save()
        return redirect ('/accounts/room/{0}'.format(room_id))
    return render (request, 'edit_room.html', {'room': room})


def sign_up_event(request, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == 'POST':
        name = request.POST['event_name']
        cmt = request.POST['discription']
        is_task = 0
        day = request.POST['data'].split()
        if request.POST['data'] != '' and request.POST['time'] != '':
            if int(day[0])<10:
                day[0]='0'+day[0]
            months = ['January,', 'February,', 'March,', 'April,', 'May,', 'June,', 'Jule,', 'August,', 'September,', 'October,', 'November,', 'December,']
            for i in range(12):
                if day[1]==months[i]:
                    day[1]=str(i+1)
                    if int(day[1])<10:
                        day[1]='0'+day[1]
            date = str(day[2]+'-'+day[1]+'-'+day[0]+' '+request.POST['time'])
        else:
            return render(request, 'sign_up_event.html', {'error': 'Write both: time and date'})
        try:
            members = list(map(lambda x: int(x), dict(request.POST)["members_send"]))
        except:
            members = []
        Event.objects.get_or_create(name=name, cmt=cmt, date=date, room=room, is_task=is_task)
        event = Event.objects.get(name=name)
        event.users.set(members)
        return redirect("/accounts/room/{0}".format(room_id))
    return render(request, 'sign_up_event.html', {'members': list(room.users.all()) + list(room.admins.all())})


def sign_up_task(request, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == 'POST':
        name = request.POST['task_name']
        cmt = request.POST['discription']
        is_task = 1 #request.POST['is_task']
        day = request.POST['data'].split()
        if request.POST['data'] != '' and request.POST['time'] != '':
            if int(day[0])<10:
                day[0]='0'+day[0]
            months = ['January,', 'February,', 'March,', 'April,', 'May,', 'June,', 'Jule,', 'August,', 'September,', 'October,', 'November,', 'December,']
            for i in range(12):
                if day[1]==months[i]:
                    day[1]=str(i+1)
                    if int(day[1])<10:
                        day[1]='0'+day[1]
            date = str(day[2] + '-' + day[1] + '-' + day[0] + ' ' + request.POST['time'])
        else:
            return render(request, 'sign_up_task.html', {'error': 'Write both: time and date'})
        members = list(map(lambda x: int(x), dict(request.POST)["members_send"]))
        Event.objects.get_or_create(name=name, cmt=cmt, date=date, room=room, is_task=is_task)
        event = Event.objects.get(name=name)
        event.users.set(members)
        return redirect("/accounts/room/{0}".format(room_id))
    return render(request, 'sign_up_task.html', {'members': list(room.users.all()) + list(room.admins.all())})


def member(request, member_id):
    if request.method == "GET":
        member = User.objects.get(id=member_id)

        return render(request, "member.html", {"member": member})


def event(request, event_id):
    if request.method == "GET":
        event = Event.objects.get(id=event_id)
        admin = 0
        if request.user.person in event.room.admins.all():
            admin = 1
        room_id = event.room.id
        room = Room.objects.get(id=room_id)
        users = set(list(room.users.all()) + list(room.admins.all()))
        event_memebrs = list(event.users.all())
        members = []
        for user in event_memebrs:
            if user in users:
                members.append(user)
        event.users.set(members)
        return render(request, 'event.html', {'admin': admin, 'event': event, 'type': 'event', 'members': list(event.users.all())})


def task(request, task_id):
    if request.method == "GET":
        task = Event.objects.get(id=task_id)
        admin = 0
        if request.user.person in task.room.admins.all():
            admin = 1
        room_id = task.room.id
        room = Room.objects.get(id=room_id)
        users = set(list(room.users.all()) + list(room.admins.all()))
        task_memebrs = list(task.users.all())
        members = []
        for user in task_memebrs:
            if user in users:
                members.append(user)
        task.users.set(members)
        return render(request, 'event.html', {'admin': admin, 'event': task, 'type': 'task', 'members': members})


def edit_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        event.name = request.POST['event_name']
        event.cmt = request.POST['discription']
        day = request.POST['data'].split()
        if request.POST['data'] != '' and request.POST['time'] != '':
            if int(day[0])<10:
                day[0]='0'+day[0]
            months = ['January,', 'February,', 'March,', 'April,', 'May,', 'June,', 'Jule,', 'August,', 'September,', 'October,', 'November,', 'December,']
            for i in range(12):
                if day[1]==months[i]:
                    day[1]=str(i+1)
                    if int(day[1])<10:
                        day[1]='0'+day[1]
            date = str(day[2]+'-'+day[1]+'-'+day[0]+' '+request.POST['time'])
            event.date=date
        event.save()
        return redirect ('/accounts/event/{0}'.format(event_id))
    return render (request, 'edit_event.html', {'event': event})


def room_notification(request, room_id):
    if request.method == "GET":
        room = Room.objects.get(id=room_id)
        return render(request, 'room_notification.html', {'members': list(room.users.all()) + list(room.admins.all())})

    if request.method == "POST":
        noti_users = list(map(lambda x: int(x), dict(request.POST)["members_send"]))
        #data = request.files['file']
        #data.save()
        room = Room.objects.get(id=room_id)
        vk = VkPlus(vk_settings.token)
        try:
            vk = VkPlus(vk_settings.token)
        except:
            return render(request, "result.html", {'text': "При отправке уведомления возникла ошибка, проверьте подключение к интернету!", 'room_id': room_id})
        users = list(room.users.all()) + list(room.admins.all())
        noti_users = set(noti_users)
        text = request.POST['message']
        er_users = []
        for user_ in users:
            if user_.id in noti_users:
                try:
                    vk.send(
                        message=text + "\n" + "//Отправлено пользователем {0} {1}".format(request.user.first_name, request.user.last_name) + " из комнаты {0} через приложение DEVENT//".format(room.name),
                        user_id=int(user_.vk_id)
                    )
                except:
                    er_users.append(user_.id)
        for i in range(len(er_users)):
            euser = er_users[i]
            member = User.objects.get(id=euser)
            er_users[i] = member.first_name + " " + member.last_name
        if len(er_users):
            return render(request, "result.html", {'text': "При отправке уведомления пользователям {0} возникла ошибка.".format(" ".join(er_users))
                                                           + "Скорей всего они ограничили отправку сообщений от именни группы приложения. Остальным пользователям уведомление успешно доставлено."
                .format(" ".join(er_users)),
                                                   'room_id': room_id})
        return render(request, "result.html", {"text": "Уведомление успешно доставлено!",
                                               "room_id": room_id})

def sign_up_event_on_user(request, member_id, room_id):
    room = Room.objects.get(id=room_id)
    if request.method == 'POST':
        name = request.POST['event_name']
        cmt = request.POST['discription']
        # date = str(request.POST['data']+' '+request.POST['time'])
        day = request.POST['data'].split()
        if request.POST['data'] != '' and request.POST['time'] != '':
            if int(day[0]) < 10:
                day[0] = '0' + day[0]
            months = ['January,', 'February,', 'March,', 'April,', 'May,', 'June,', 'Jule,', 'August,', 'September,',
                      'October,', 'November,', 'December,']
            for i in range(12):
                if day[1] == months[i]:
                    day[1] = str(i + 1)
                    if int(day[1]) < 10:
                        day[1] = '0' + day[1]
            date = str(day[2] + '-' + day[1] + '-' + day[0] + ' ' + request.POST['time'])
        else:
            return render(request, 'sign_up_event.html', {'error': 'Write both: time and date'})
        member = Person.objects.get(id=member_id)
        members = [member]
        Event.objects.get_or_create(name=name, cmt=cmt, date=date, room=room, is_task=True)
        event = Event.objects.get(name=name)
        event.users.set(members)
        return redirect("/accounts/room/{0}".format(room_id))
    return render(request, 'sign_up_event_on_user.html', {'member': Person.objects.get(id=member_id)})

#ajax:

def delete_user_from_room(request, member_id, room_id):
    room = Room.objects.get(id=room_id)
    users = []
    for user in room.users.all():
        if user.id != member_id:
            users.append(user)
    try:
        room.users.set(users)
        return HttpResponse("1")
    except:
        return HttpResponse("0")


def end_task(request, member_id, task_id):
    task = Event.objects.get(id=task_id)
    members = list(task.users.all())
    users = []
    for member in members:
        if member.id != member_id:
            users.append(member)
    try:
        task.users.set(users)
        return HttpResponse("1")
    except:
        return HttpResponse("0")


def end_event(request, room_id, event_id):
    event = Event.objects.get(id=event_id)
    try:
        event.users.set([])
        return HttpResponse("1")
    except:
        return HttpResponse("0")







    
