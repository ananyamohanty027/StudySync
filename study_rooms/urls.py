from django.urls import path
from . import views

app_name = 'study_rooms'

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.create_room, name='create_room'),
    path('verify-teacher/', views.verify_teacher, name='verify_teacher'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:pk>/join/', views.join_room, name='join_room'),
    path('rooms/<int:pk>/leave/', views.leave_room, name='leave_room'),
    path('rooms/<int:pk>/share-resource/', views.share_resource, name='share_resource'),
    path('rooms/<int:pk>/send-message/', views.send_message, name='send_message'),
    path('rooms/<int:pk>/create-document/', views.create_document, name='create_document'),
    path('documents/<int:pk>/', views.document_detail, name='document_detail'),
    path('rooms/<int:pk>/create-study-session/', views.create_study_session, name='create_study_session'),
    path('study-sessions/<int:pk>/', views.study_session_detail, name='study_session_detail'),
    path('study-sessions/<int:pk>/end/', views.end_study_session, name='end_study_session'),
]