from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.username

class Teacher(models.Model):
    teacher_id = models.CharField(max_length=10, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} (ID: {self.teacher_id})"

class StudyRoom(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=10)
    is_private = models.BooleanField(default=False)
    password = models.CharField(max_length=128, blank=True, null=True)
    has_video_call = models.BooleanField(default=True)
    has_screen_sharing = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='participants')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_moderator = models.BooleanField(default=False)
    is_speaking = models.BooleanField(default=False)
    is_screen_sharing = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'room']

    def __str__(self):
        return f"{self.user.username} in {self.room.name}"

class SharedResource(models.Model):
    RESOURCE_TYPES = (
        ('document', 'Document'),
        ('link', 'Link'),
        ('note', 'Note'),
        ('other', 'Other'),
    )

    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='resources')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='study_resources/', blank=True, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"

class Document(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_shared = models.BooleanField(default=True)
    is_being_edited = models.BooleanField(default=False)
    current_editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='editing_documents')

    def __str__(self):
        return self.title

class DocumentEdit(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='edits')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Edit by {self.user.username} at {self.timestamp}"

class VideoCall(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='video_calls')
    started_by = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=10)

    def __str__(self):
        return f"Video call in {self.room.name}"

class ScreenShare(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='screen_shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Screen share by {self.shared_by.username} in {self.room.name}"

class StudySession(models.Model):
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='study_sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    has_video_call = models.BooleanField(default=True)
    has_screen_sharing = models.BooleanField(default=True)
    has_document_collaboration = models.BooleanField(default=True)

    def __str__(self):
        return self.title
