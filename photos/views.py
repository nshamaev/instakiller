# -*- coding: utf-8 -*-
from photos.filters import PhotoFilter
from rest_framework import views, viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter, DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from photos.serializers import PhotoWithoutPathSerializer, PhotoSerializer
from photos.serializers import PhotoUploadSerializer


class PhotoUploadView(views.APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def post(self, request, format=None):
        context = {
            "request": self.request,
        }
        serializer = PhotoUploadSerializer(data=request.data, context=context)
        if serializer.is_valid():
            photo = serializer.save()
            return Response({"id": photo.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class PhotoViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = PhotoSerializer
    http_method_names = ['get', 'put', 'delete']
    filter_backends = (OrderingFilter, DjangoFilterBackend, SearchFilter)
    filter_class = PhotoFilter
    search_fields = ('name', )
    ordering_fields = ('name', 'created_at')

    def get_queryset(self):

        return self.request.user.photo_set.all()

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.method == 'PUT':
            serializer_class = PhotoWithoutPathSerializer

        return serializer_class
