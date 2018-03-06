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


def goto(request):
    id_ = request.user.id
    if id_:
        return redirect('/accounts/member/{0}'.format(id_))
    return redirect('/login')


def sign_up(request):
    if request.method == 'POST':
        name = request.POST['name']
        lastname = request.POST['lastname']
        login = request.POST['login']
        try:
            vk_id = url2vk_id(request.POST['VK'])
        except:
            vk_id = -1
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


def add_user(request, room_id):
    if request.method == 'POST':
        name = request.POST['name']
        last_name = request.POST['lastname']
        id_ = request.POST['id']
        grade = request.POST['grade']
        let = request.POST['let']
        users = list(Person.objects.all())
        if name:
            users = [user if user.user.first_name == name else "" for user in users]
        if last_name:
            users = [user if user and user.user.last_name == last_name else "" for user in users]
        if id_:
            users = [user if user and user.id == int(id_) else "" for user in users]
        '''
        if grade:
            params['grade'] = grade
        if let:
            params['letter'] = let
        '''
        members = []
        room = Room.objects.get(id=room_id)
        room_members = set(list(room.users.all()) + list(room.admins.all()))
        for user in users:
            if user and (user not in room_members):
                members.append((user.id, user.user.first_name, user.user.last_name, '-', '-'))
        return render(request, 'add_user.html', {'c': range(1, 12),
                                                 'room_id': room_id,
                                                 'letters': ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Н', 'М'],
                                                 'members': members})
    if request.method == "GET":
        users = set(list(Person.objects.all()))
        room = Room.objects.get(id=room_id)
        room_users = set(list(room.users.all()))
        users = list(users - room_users)
        members = []
        for user in users:
            members.append((user.id, user.user.first_name, user.user.last_name, '-', '-'))
        return render(request, 'add_user.html', {'c' : range(1, 12),
                                                'room_id': room_id,
                                                 'members': members,
                                                'letters': ['А', 'Б', 'В', 'Г' , 'Д', 'Е', 'Н', 'М']})


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
    user = request.user
    if request.method == "POST":
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        if request.POST['password'] != '' and request.POST['repassword'] != '':
            if request.POST['password'] == request.POST['repassword']:
                user.set_password(request.POST['password'])
                user.save()
                return redirect('/login')
            else:
                return render(request, 'edit_user.html', {'error': 'Пароли не совпадают',
                                                          'events': list(user.person.events.filter(is_task=0)),
                                                          'tasks': list(user.person.events.filter(is_task=1)),
                                                          'groups': list(user.person.agroups.all()) + list(
                                                              user.person.ugroups.all())})
        user.save()
        return redirect('/accounts/profile')
    return render(request, 'edit_user.html', {'user': user, 'events': list(user.person.events.filter(is_task=0)),
                                              'tasks': list(user.person.events.filter(is_task=1)),
                                              'groups': list(user.person.agroups.all()) + list(
                                                  user.person.ugroups.all())})


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
        return render(request, "room.html", {'error': "",
                                             'data': data,
                                             'room': room,
                                             'members_and_admins': list(room.users.all()) + list(room.admins.all()),
                                             'members': list(room.users.all()),
                                             'admins': list(room.admins.all()),
                                             'admin': admin,
                                             'events': events,
                                             'tasks': tasks,
                                             'discription': room.cmt,
                                             })

    elif request.method=="POST" and request.POST.get("form_type") == "event":
        room = Room.objects.get(id=room_id)
        name = request.POST['event_name']
        cmt = request.POST['discription']
        is_task = 0
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
            return redirect("/accounts/room/{0}".format(room_id))
        try:
            members = list(map(lambda x: int(x), dict(request.POST)["members_send"]))
        except:
            members = []
        Event.objects.get_or_create(name=name, cmt=cmt, date=date, room=room, is_task=is_task)
        event = Event.objects.get(name=name)
        event.users.set(members)
        try:
            users_send = list(event.users.all())
            text = "Новое мероприятие {0} в группе {1}".format(event.name, room.name)
            vk = VkPlus(vk_settings.token)
            for user_ in users_send:
                try:
                    vk.send(
                        message=text + "\n" + "//Отправлено через приложение DEVENT//",
                        user_id=int(user_.vk_id)
                    )
                except:
                    pass
        except:
            pass
        return redirect("/accounts/room/{0}".format(room_id))
    elif request.method == "POST" and request.POST.get("form_type") == "noti":
        noti_users = list(map(lambda x: int(x), dict(request.POST)["members_send"]))
        room = Room.objects.get(id=room_id)
        try:
            vk = VkPlus(vk_settings.token)
        except:
            return render(request, "result.html",
                          {'text': "При отправке уведомления возникла ошибка, проверьте подключение к интернету!",
                           'id': room_id,
                           'type': 'room'})
        users = list(room.users.all()) + list(room.admins.all())
        noti_users = set(noti_users)
        text = request.POST['message']
        er_users = []
        for user_ in users:
            if user_.id in noti_users:
                try:
                    vk.send(
                        message=text + "\n" + "//Отправлено пользователем {0} {1}".format(request.user.first_name,
                                                                                          request.user.last_name) + " из комнаты {0} через приложение DEVENT//".format(
                            room.name),
                        user_id=int(user_.vk_id)
                    )
                except:
                    er_users.append(user_.id)
        for i in range(len(er_users)):
            euser = er_users[i]
            member = User.objects.get(id=euser)
            er_users[i] = member.first_name + " " + member.last_name
        if len(er_users):
            return render(request, "result.html", {
                'text': "При отправке уведомления пользователям {0} возникла ошибка.".format(" ".join(er_users))
                        + "Скорей всего они ограничили отправку сообщений от именни группы приложения. Остальным пользователям уведомление успешно доставлено."
                          .format(", ".join(er_users)),
                'id': room_id,
                'type': 'room',
            })
        return render(request, "result.html", {"text": "Уведомление успешно доставлено!",
                                               "id": room_id,
                                               'type': 'room'})


    elif request.method == "POST" and request.POST.get("form_type") == "task":
        room = Room.objects.get(id=room_id)
        name = request.POST['task_name']
        cmt = request.POST['discription']
        is_task = 1
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
            return redirect("/accounts/room/{0}".format(room_id))
        members = list(map(lambda x: int(x), dict(request.POST)["members_send"]))
        Event.objects.get_or_create(name=name, cmt=cmt, date=date, room=room, is_task=is_task)
        task = Event.objects.get(name=name)
        task.users.set(members)
        try:
            users_send = list(task.users.all())
            text = "У вас новая задача {0}".format(task.name)
            vk = VkPlus(vk_settings.token)
            for user_ in users_send:
                try:
                    vk.send(
                        message=text + "\n" + "//Отправлено через приложение DEVENT//",
                        user_id=int(user_.vk_id)
                    )
                except:
                    pass
        except:
            pass
        return redirect("/accounts/room/{0}".format(room_id))
    elif request.method == "POST" and request.POST.get("form_type") == "task_on_user":
        room = Room.objects.get(id=room_id)
        name = request.POST['task_name_on_user']
        cmt = request.POST['discription']
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
            return redirect("/accounts/room/{0}".format(room_id))
        member = Person.objects.get(id=request.POST['member_id'])
        members = [member]
        Event.objects.get_or_create(name=name, cmt=cmt, date=date, room=room, is_task=True)
        task = Event.objects.get(name=name, cmt=cmt, date=date, room=room, is_task=True)
        task.users.set(members)
        try:
            users_send = [member]
            text = "У вас новая задача {0}".format(task.name)
            vk = VkPlus(vk_settings.token)
            for user_ in users_send:
                try:
                    vk.send(
                        message=text + "\n" + "//Отправлено через приложение DEVENT//",
                        user_id=int(user_.vk_id)
                    )
                except:
                    pass
        except:
            pass
        return redirect("/accounts/room/{0}".format(room_id))
    elif request.method=="POST" and request.POST.get("form_type")=="leave_room":
        room = Room.objects.get(id=room_id)
        users = list(room.users.all())
        users.remove(request.user.person)
        room.users.set(users)
        return redirect("/accounts/profile/")


def edit_room(request, room_id):
    room = Room.objects.get(id=room_id)
    events = list(room.events.filter(is_task=0))
    tasks = list(room.events.filter(is_task=1))
    users_tasks = []
    users = list(room.users.all()) + list(room.admins.all())
    for user in users:
        user_tasks = []
        for event in list(room.events.filter(is_task=1)):
            if user in event.users.all():
                user_tasks.append(event)
        users_tasks.append(user_tasks)
        data = list(zip(users_tasks, users))
    if request.method == 'POST' and request.POST.get("form_type") == "edit_room":
        room.name = request.POST['room_name']
        room.cmt = request.POST['cmt']
        room.save()
        return redirect ('/accounts/room/{0}'.format(room_id))
    elif request.method == "POST" and request.POST.get("form_type") == "delete_room":
        for person in list(room.users.all()):
            rooms=list(person.ugroups.all())
            rooms.remove(room)
            person.ugroups.set(rooms)
        for admin in list(room.admins.all()):
            rooms = list(admin.agroups.all())
            rooms.remove(room)
            admin.agroups.set(rooms)
        for event in list(room.events.all()):
            for person in list(event.users.all()):
                events=list(person.events.all())
                events.remove(event)
                person.events.set(events)
            event.delete()
        room.delete()
        return redirect("/accounts/profile")
    return render (request, 'edit_room.html', {'room': room,
                                               'data': data,
                                               'members': list(room.users.all()),
                                               'admins': list(room.admins.all()),
                                               'events': list(room.events.filter(is_task=0)),
                                               'tasks': list(room.events.filter(is_task=1))})


def member(request, member_id):
    if request.method == "GET":
        if request.user.id == member_id:
            return redirect("/accounts/profile/")
        member = User.objects.get(id=member_id)
        return render(request, "member.html", {"member": member})


def event(request, event_id):
    event = Event.objects.get(id=event_id)
    room_id = event.room.id
    room = Room.objects.get(id=room_id)
    room_members = list(room.users.all()) + list(room.admins.all())
    admin = 0
    if request.user.person in event.room.admins.all():
        admin = 1
    room = Room.objects.get(id=room_id)
    users = set(list(room.users.all()) + list(room.admins.all()))
    event_memebrs = list(event.users.all())
    members = []
    for user in event_memebrs:
        if user in users:
            members.append(user)
    event.users.set(members)
    if request.method == "GET":
        new_members = []
        room_members.extend((room.admins.all()))
        for member in room_members:
            if member not in members:
                new_members.append(member)

        return render(request, 'event.html', {'admin': admin,
                                              'event': event,
                                              'type': 'event',
                                              'members': list(event.users.all()),
                                              'new_members': new_members})

    elif request.method == "POST" and request.POST.get("form_type") == "add":
        new_members = list(map(lambda x: int(x), dict(request.POST)["new_members"]))
        event.users.set(list(event.users.all()) + new_members)
        members = list(event.users.all())
        new_members = []
        for member in room_members:
            if member not in members:
                new_members.append(member)
        return render(request, 'event.html', {'admin': admin,
                                              'event': event,
                                              'type': 'event',
                                              'members': list(event.users.all()),
                                              'new_members': new_members})

    elif request.method == "POST" and request.POST.get("form_type") == "noti":
        noti_users = list(map(lambda x: int(x), dict(request.POST)["members_send"]))
        room = Room.objects.get(id=room_id)
        try:
            vk = VkPlus(vk_settings.token)
        except:
            return render(request, "result.html",
                          {'text': "При отправке уведомления возникла ошибка, проверьте подключение к интернету!",
                           'id': event_id,
                           'type': 'event'})
        users = list(room.users.all()) + list(room.admins.all())
        noti_users = set(noti_users)
        text = request.POST['message']
        er_users = []
        for user_ in users:
            if user_.id in noti_users:
                try:
                    vk.send(
                        message=text + "\n" + "//Отправлено пользователем {0} {1}".format(request.user.first_name,
                                                                                          request.user.last_name) + " из комнаты {0} через приложение DEVENT//".format(
                            room.name),
                        user_id=int(user_.vk_id)
                    )
                except:
                    er_users.append(user_.id)
        for i in range(len(er_users)):
            euser = er_users[i]
            member = User.objects.get(id=euser)
            er_users[i] = member.first_name + " " + member.last_name
        if len(er_users):
            return render(request, "result.html", {
                'text': "При отправке уведомления пользователям {0} возникла ошибка.".format(" ".join(er_users))
                        + "Скорей всего они ограничили отправку сообщений от именни группы приложения. Остальным пользователям уведомление успешно доставлено."
                          .format(", ".join(er_users)),
                'id': event_id,
                'type': 'event'})
        return render(request, "result.html", {"text": "Уведомление успешно доставлено!",
                                               "id": event_id,
                                               'type': 'event'})
    elif request.method == "POST" and request.POST.get("form_type") == "leave_event":
        events=list(request.user.person.events.all())
        events.remove(event)
        request.user.person.events.set(events)
        return redirect("/accounts/room/{0}".format(room_id))


def task(request, task_id):
    if request.method == "GET":
        task = Event.objects.get(id=task_id)
        admin = 0
        room_id = task.room.id
        room = Room.objects.get(id=room_id)
        if request.user.person in task.room.admins.all():
            admin = 1
        users = set(list(room.users.all()) + list(room.admins.all()))
        task_memebrs = list(task.users.all())
        members = []
        for user in task_memebrs:
            if user in users:
                members.append(user)
        task.users.set(members)
        new_members = []
        room_members = list(room.users.all()) + list(room.admins.all())
        for member in room_members:
            if member not in members:
                new_members.append(member)
        return render(request, 'event.html', {'admin': admin,
                                              'event': task,
                                              'type': 'task',
                                              'members': members,
                                              'new_members': new_members})
    if request.method == "POST":
        task = Event.objects.get(id=task_id)
        room_id = task.room.id
        admin = 0
        room = Room.objects.get(id=room_id)
        room_members = list(room.users.all())
        if request.user.person in task.room.admins.all():
            admin = 1
        users = set(list(room.users.all()) + list(room.admins.all()))
        task_memebrs = list(task.users.all())
        members = []
        for user in task_memebrs:
            if user in users:
                members.append(user)
        task.users.set(members)
        new_members = list(map(lambda x: int(x), dict(request.POST)["new_members"]))
        nm = list(task.users.all()) + new_members
        task.users.set(nm)
        members = list(task.users.all())
        new_members = []
        for member in room_members:
            if member not in members:
                new_members.append(member)
        return render(request, 'event.html', {'admin': admin,
                                              'event': task,
                                              'type': 'task',
                                              'members': members,
                                              'new_members': new_members})


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


#ajax:

def check_login(request, login):
    users = list(Person.objects.all())
    users = list(map(lambda x: x.login, users))
    if login not in users:
        return HttpResponse("1")
    return HttpResponse("0")


def add_one_user(request, user_id, room_id):
    room = Room.objects.get(id=room_id)
    id_ = user_id
    users = list(room.users.all())
    try:
        user = Person.objects.get(id=id_)
        if user not in users:
            room.users.set(list(room.users.all()) + [user])
    except:
        return HttpResponse("0")
    member = Person.objects.get(id=id_)
    users_send = list(room.admins.all())
    try:
        text = "Пользователь {0} успешно добавлен в комнату {1}".format(member, room.name)
        vk = VkPlus(vk_settings.token)
        for user_ in users_send:
            try:
                vk.send(
                    message=text + "\n" + "//Отправлено через приложение DEVENT//".format(
                        room.name),
                    user_id=int(user_.vk_id)
                )
            except:
                pass
    except:
        pass
    return HttpResponse("1")


def delete_user_from_room(request, member_id, room_id):
    room = Room.objects.get(id=room_id)
    users_send = list(room.admins.all())
    member = Person.objects.get(id=member_id)
    users = []
    for user in room.users.all():
        if user.id != member_id:
            users.append(user)
    try:
        room.users.set(users)
        try:
            text = "Пользователь {0} успешно удален из комнаты {1}".format(member, room.name)
            vk = VkPlus(vk_settings.token)
            for user_ in users_send:
                try:
                    vk.send(
                        message=text + "\n" + "//Отправлено через приложение DEVENT//".format(
                            room.name),
                        user_id=int(user_.vk_id)
                    )
                except:
                    pass
        except:
            pass
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
        try:
            member = Person.objects.get(id=member_id)
            users_send = [member]
            text = "Вы успешно выполнили задачу {0}".format(task.name)
            vk = VkPlus(vk_settings.token)
            for user_ in users_send:
                try:
                    vk.send(
                        message=text + "\n" + "//Отправлено через приложение DEVENT//",
                        user_id=int(user_.vk_id)
                    )
                except:
                    pass
        except:
            pass
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







    
