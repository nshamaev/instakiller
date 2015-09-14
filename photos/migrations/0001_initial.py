# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import colorful.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', models.ImageField(upload_to=b'images')),
                ('name', models.CharField(max_length=255)),
                ('border_color', colorful.fields.RGBColorField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
