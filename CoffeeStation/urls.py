from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('backend.urls')),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
