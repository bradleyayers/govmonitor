# coding=utf-8
from .models import *
from django.contrib import admin


models = (Issue, Party, Reference, Tag, UserProfile, View, Vote)
map(admin.site.register, models)
