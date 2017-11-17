from django.contrib.auth import get_user_model
from django import forms
from .models import Person

class SignupForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ('login', 'password', 'vk_id', 'first_name', 'picture')

    def save(self, user):
        Person.save()
        user.save()