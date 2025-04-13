from django.contrib import admin
from .models import StudyRoom, Participant, SharedResource, ChatMessage, Document, DocumentEdit

@admin.register(StudyRoom)
class StudyRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'is_private', 'created_at', 'is_active', 'max_participants')
    list_filter = ('is_private', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'host__username')
    date_hierarchy = 'created_at'

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'joined_at', 'is_active', 'is_moderator')
    list_filter = ('is_active', 'is_moderator', 'joined_at')
    search_fields = ('user__username', 'room__name')
    date_hierarchy = 'joined_at'

@admin.register(SharedResource)
class SharedResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'room', 'shared_by', 'resource_type', 'shared_at')
    list_filter = ('resource_type', 'shared_at')
    search_fields = ('title', 'room__name', 'shared_by__username')
    date_hierarchy = 'shared_at'

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'message', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('message', 'user__username', 'room__name')
    date_hierarchy = 'timestamp'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'room', 'created_by', 'created_at', 'last_modified', 'is_shared')
    list_filter = ('is_shared', 'created_at', 'last_modified')
    search_fields = ('title', 'content', 'created_by__username', 'room__name')
    date_hierarchy = 'created_at'

@admin.register(DocumentEdit)
class DocumentEditAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('document__title', 'user__username', 'content')
    date_hierarchy = 'timestamp'
