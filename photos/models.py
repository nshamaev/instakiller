# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from colorful.fields import RGBColorField


class Photo(models.Model):
    owner = models.ForeignKey(User)
    photo = models.ImageField(upload_to='images')
    name = models.CharField(max_length=255)
    border_color = RGBColorField()
    created_at = models.DateTimeField(auto_now_add=True)
