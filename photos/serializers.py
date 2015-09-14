# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from photos.models import Photo


class PhotoUploadSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Photo
        fields = ('id', 'name', 'photo', 'owner', 'border_color', 'created_at')


class PhotoSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(use_url=True)

    class Meta:
        model = Photo
        fields = ('id', 'name', 'photo', 'border_color', 'created_at')


class PhotoWithoutPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('name', 'border_color')
