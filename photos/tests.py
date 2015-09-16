# -*- coding: utf-8 -*-
from datetime import timedelta
from StringIO import StringIO
from django.utils import timezone
from PIL import Image
from django.contrib.auth.models import User
from django.core.files import File
from photos.serializers import PhotoSerializer
from photos.views import PhotoUploadView, PhotoViewSet
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.test import force_authenticate
from photos.models import Photo


class PhotoTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory(enforce_csrf_checks=True)
        self.user = User.objects.create_user(username='testuser',
                                             email='user@test.com',
                                             password='password')
        self.image = {
            "name": "testname",
            "border_color": "FFFFFF",
            "photo": self.create_image_file()
        }

    def tearDown(self):
        for photo in Photo.objects.all():
            photo.delete()

    def test_photo_upload(self):
        """
        Ensure we can upload a new photo.
        """
        request = self.factory.post(reverse('photo-upload'), data=self.image)
        force_authenticate(request, user=self.user)
        response = PhotoUploadView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Photo.objects.count(), 1)
        self.assertEqual(Photo.objects.get().name, 'testname')

    def test_photo_detail(self):
        """
        Ensure we can view photo detail by id
        """
        photo = self.create_photo_model()
        response = self.make_request('get', 'retrieve', pk=photo.id)
        response_json = PhotoSerializer(photo).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            response_json.pop("photo"),
            response.data.pop("photo")
        )
        self.assertEqual(response.data, response_json)

    def test_update_photo(self):
        """
        Ensure we can update photo name and border's color
        """
        photo = self.create_photo_model()
        update_data = {
            "name": "newphotoname",
            "border_color": "AAAAAA"
        }
        response = self.make_request('put', 'update', data=update_data,
                                     pk=photo.id)
        photo_model = Photo.objects.get(pk=photo.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(photo_model.name, update_data["name"])
        self.assertEqual(photo_model.border_color, update_data["border_color"])

    def test_delete_photo(self):
        """
        Ensure we can delete photo by id
        """
        photo = self.create_photo_model()
        response = self.make_request('delete', 'destroy', pk=photo.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Photo.objects.filter(pk=photo.id).exists())

    def test_sort_photos(self):
        """
        Ensure we can sort photos by name or datetime
        """
        photos_data = [
            ("cool", timezone.now() - timedelta(days=2)),
            ("deep", timezone.now()),
            ("aromatic", timezone.now() - timedelta(days=1))
        ]

        photos_id = [self.create_photo_model(name=name, created_at=date).id
                     for name, date in photos_data]

        response = self.make_request('get', 'list', data={"ordering": "name"})
        self.assertEqual(
            [photos_id[2], photos_id[0], photos_id[1]],
            [photo['id'] for photo in response.data['results']]
        )

        response = self.make_request('get', 'list',
                                     data={"ordering": "created_at"})
        self.assertSequenceEqual(
            [photos_id[0], photos_id[2], photos_id[1]],
            [photo['id'] for photo in response.data['results']]
        )

    def test_paginate_photos(self):
        """
        Ensure we can paginate by 10, 50, 100 photos
        """
        [self.create_photo_model() for i in range(201)]

        response = self.make_request('get', 'list',
                                     data={"page": 1, "per_page": 10})
        self.assertEqual(10, len(response.data["results"]))

        response = self.make_request('get', 'list',
                                     data={"page": 1, "per_page": 50})
        self.assertEqual(50, len(response.data["results"]))

        response = self.make_request('get', 'list',
                                     data={"page": 1, "per_page": 100})
        self.assertEqual(100, len(response.data["results"]))

        response = self.make_request('get', 'list',
                                     data={"page": 2, "per_page": 100})
        self.assertEqual(100, len(response.data["results"]))

        response = self.make_request('get', 'list',
                                     data={"page": 3, "per_page": 100})
        self.assertEqual(1, len(response.data["results"]))

    def test_filter_by_date(self):
        """
        Ensure we can filter photos by concrete date
        """
        photos_dates = [timezone.now() - timedelta(days=2),
                        timezone.now() - timedelta(days=1)]

        photos_id = [self.create_photo_model(created_at=date).id
                     for date in photos_dates]
        data = {"created_at": photos_dates[0].date()}
        response = self.make_request('get', 'list', data=data)

        self.assertEqual(photos_id[0], response.data["results"][0]["id"])

        data = {"created_at": photos_dates[1].date()}
        response = self.make_request('get', 'list', data=data)
        self.assertEqual(photos_id[1], response.data["results"][0]["id"])

    def test_search_by_part_name(self):
        """
        Ensure we can search by part name of photo
        """
        first_photo = self.create_photo_model(
            name="very beautiful picture of the area around my house"
        )
        self.create_photo_model(
            name="chanterelle eats the mouse near my house"
        )
        response = self.make_request('get', 'list', data={"search": "area"})
        self.assertEqual(first_photo.id, response.data["results"][0]["id"])

        response = self.make_request('get', 'list', data={"search": "house"})
        self.assertEqual(2, len(response.data["results"]))

        response = self.make_request('get', 'list', data={"search": "test"})
        self.assertEqual(0, len(response.data["results"]))

    def test_filter_by_date_range(self):
        """
        Ensure we can filter photos by range date
        """
        photos_dates = [
            timezone.now() - timedelta(days=6),
            timezone.now() - timedelta(days=2),
            timezone.now() - timedelta(days=1)
        ]
        photos_id = [self.create_photo_model(created_at=date).id
                     for date in photos_dates]
        data = {"min_date": timezone.now().date() - timedelta(days=3)}
        response = self.make_request('get', 'list', data=data)
        self.assertListEqual(
            sorted(photos_id[1:]),
            sorted([photo["id"] for photo in response.data["results"]])
        )

    def test_xml_format(self):
        """
        Ensure we can receive photos in xml format"
        """
        photo = self.create_photo_model()
        response = self.make_request('get', 'list', data={'format': 'xml'})
        self.assertEqual(response.accepted_media_type, 'application/xml')
        self.assertEqual(photo.id, response.data['results'][0]["id"])

    def make_request(self, method, action, data=None, pk=None, user=None):
        if user is None:
            user = self.user
        request = getattr(self.factory, method)(reverse('photos-list'),
                                                data=data)
        force_authenticate(request, user=user)
        return PhotoViewSet.as_view({method: action})(request, pk=pk)

    def create_image_file(self, name='test.png'):
        file_obj = StringIO()
        image = Image.new("RGBA", (200, 200), (255, 0, 0, 0))
        image.save(file_obj, 'png')
        file_obj.seek(0)
        return File(file_obj, name=name)

    def create_photo_model(self, name='testname', border_color="#FFFFFF",
                           created_at=None):
        photo = Photo(
            owner=self.user,
            photo=self.create_image_file(),
            name=name,
            border_color=border_color,
        )
        photo.save()
        if created_at is not None:
            Photo.objects.filter(pk=photo.pk).update(created_at=created_at)
        return photo
