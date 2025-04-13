from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from study_rooms.views import home, register, profile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('study_rooms/', include('study_rooms.urls')),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='study_rooms/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
] 