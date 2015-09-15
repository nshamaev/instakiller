# -*- coding: utf-8 -*-
import os
from django.core.files.storage import default_storage
from django.db.models import ImageField


def file_cleanup(sender, **kwargs):
    """
    File cleanup callback used to emulate the old delete
    behavior using signals. Initially django deleted linked
    files when an object containing a File/ImageField was deleted.
    """
    for fieldname in sender._meta.get_all_field_names():
        try:
            field = sender._meta.get_field(fieldname)
        except:
            field = None
        if field and isinstance(field, ImageField):
            instance = kwargs['instance']
            f = getattr(instance, fieldname)
            m = instance.__class__._default_manager
            if hasattr(f, 'path') and os.path.exists(f.path)\
            and not m.filter(**{'%s__exact' % fieldname: getattr(instance, fieldname)})\
            .exclude(pk=instance._get_pk_val()):
                try:
                    default_storage.delete(f.path)
                except:
                    pass
