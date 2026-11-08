import pprint

from django.contrib import admin
from django.contrib.auth.models import User

from .models import Pacienti, Ecografii


admin.site.register(Pacienti)
admin.site.register(Ecografii)




