from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from photos import views
from photos.views import PhotoViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'photos', PhotoViewSet, base_name='photos')

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^photos/upload', views.PhotoUploadView.as_view(), name='photo-upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += router.urls
