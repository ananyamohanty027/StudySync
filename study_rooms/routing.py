from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/video_call/(?P<room_id>\w+)/$', consumers.VideoCallConsumer.as_asgi()),
    re_path(r'ws/screen_share/(?P<room_id>\w+)/$', consumers.ScreenShareConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
