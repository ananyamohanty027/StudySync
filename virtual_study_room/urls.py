"""
URL configuration for virtual_study_room project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from study_rooms.views import signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('study_rooms.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='account_login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='study_rooms:home'), name='account_logout'),
    path('accounts/signup/', signup, name='account_signup'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
