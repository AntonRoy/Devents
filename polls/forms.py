'''
from django import forms

from .models import *

class SignInUser (forms.ModelForm):
    class Meta:
        model = User
        fields = ('login', 'password')
'''