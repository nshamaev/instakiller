# -*- coding: utf-8 -*-
import django_filters
from photos.models import Photo


class PhotoFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(name='created_at', lookup_type="contains")
    min_date = django_filters.DateTimeFilter(name="created_at",lookup_type='gte')
    max_date = django_filters.DateTimeFilter(name="created_at",lookup_type='lt')

    class Meta:
        model = Photo
        fields = ['created_at', 'min_date', 'max_date']
