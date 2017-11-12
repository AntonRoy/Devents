from django.contrib.auth.models import User
from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    img = models.ImageField(default="default.png", blank=True)
    vk_id = models.IntegerField(null=True, blank=True)
    login = models.CharField(max_length=40)
    password = models.CharField(max_length=40)
    def __str__(self):
        return self.login


class Room(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    img = models.ImageField(default="team_default.png", blank=True)
    cmt = models.TextField(default="Cool Room", blank=True)
    admins = models.ManyToManyField(User, blank=True, related_name='admins')
    users = models.ManyToManyField(User, blank=True, related_name='users')
    def __str__(self):
        return self.name

class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    cmt = models.TextField(default="Cool Event", blank=True)
    img = models.ImageField(default="event_default.png", blank=True)
    room = models.ForeignKey(Room)
    users = models.ManyToManyField(User, blank=True)
    def __str__(self):
        return self.name

