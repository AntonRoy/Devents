from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.contrib import admin
from datetime import datetime

class School(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Class(models.Model):
    digit = models.IntegerField(default=-1, blank=True)
    letter = models.CharField(max_length=5, blank=True, default="А")
    school = models.ForeignKey(School, models.SET_NULL, related_name="classes", blank=True, null=True)
    def __str__(self):
        return self.digit+self.letter

class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='person')
    id = models.AutoField(primary_key=True)
    img = models.ImageField(default="default.png", blank=True)
    vk_id = models.CharField(max_length=40, null=True, blank=True)
    tg_id = models.CharField(max_length=40, null=True, blank=True)
    school = models.ForeignKey(School, models.SET_NULL, related_name="school_users", blank=True, null=True)
    class_room = models.ForeignKey(School, models.SET_NULL, related_name="class_users", blank=True, null=True)
    # log/in = models.CharField(max_length=40)
    def __str__(self):
        return self.user.first_name+" "+self.user.last_name


class Room(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    img = models.ImageField(default="team_default.png", blank=True)
    cmt = models.TextField(default="Cool Room", blank=True)
    admins = models.ManyToManyField(Person, db_table='adimnrooms', blank=True, related_name='agroups')
    users = models.ManyToManyField(Person, db_table="userrooms", blank=True, related_name='ugroups')
    def __str__(self):
        return self.name

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    cmt = models.TextField(default="Cool Event", blank=True)
    img = models.ImageField(default="event_default.png", blank=True)
    room = models.ForeignKey(Room, models.CASCADE,related_name='events')
    users = models.ManyToManyField(Person, blank=True, related_name='events')
    date = models.DateTimeField(auto_now=False, auto_now_add=False, default=datetime.now)
    is_task = models.BooleanField(default=False)
    def __str__(self):
        return self.name

