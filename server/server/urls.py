from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# Api router
router = routers.DefaultRouter()

urlpatterns = [
    # Admin routes
    path('admin/', admin.site.urls),

    # Api routes
    path('api/', include('authentication.urls')),
    path('api/', include(router.urls)),
]
