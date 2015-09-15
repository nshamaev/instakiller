# -*- coding: utf-8 -*-
import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from colorful.fields import RGBColorField
from photos.utils import file_cleanup


def get_upload_path(instance, filename):
    return os.path.join(
      "user_%d" % instance.owner.id, filename)


class Photo(models.Model):
    owner = models.ForeignKey(User)
    photo = models.ImageField(upload_to=get_upload_path)
    name = models.CharField(max_length=255)
    border_color = RGBColorField()
    created_at = models.DateTimeField(auto_now_add=True)

post_delete.connect(file_cleanup, sender=Photo,
                    dispatch_uid="photos.photo.cleanup")
