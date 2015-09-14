from django.conf.urls import include, url
from photos import views
from photos.views import PhotoViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'photos', PhotoViewSet, base_name='photos')

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^photos/upload', views.PhotoUploadView.as_view()),
]

urlpatterns += router.urls
