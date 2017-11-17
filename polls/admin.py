from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


from .models import Room, Event, Person

class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline, )



admin.site.register(Room)
admin.site.register(Event)
admin.site.register(Person)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Register your models here.
