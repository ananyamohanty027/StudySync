from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import StudyRoom, SharedResource, Document, VideoCall, ScreenShare, StudySession

class StudyRoomForm(forms.ModelForm):
    class Meta:
        model = StudyRoom
        fields = ['name', 'description', 'max_participants', 'is_private', 'password', 'has_video_call', 'has_screen_sharing']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'password': forms.PasswordInput(render_value=True),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_private = cleaned_data.get('is_private')
        password = cleaned_data.get('password')
        
        if is_private and not password:
            self.add_error('password', 'Password is required for private rooms')
        
        return cleaned_data

class ResourceForm(forms.ModelForm):
    class Meta:
        model = SharedResource
        fields = ['title', 'resource_type', 'file', 'link', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        resource_type = cleaned_data.get('resource_type')
        file = cleaned_data.get('file')
        link = cleaned_data.get('link')
        content = cleaned_data.get('content')
        
        if resource_type == 'document' and not file:
            self.add_error('file', 'Please upload a document')
        elif resource_type == 'link' and not link:
            self.add_error('link', 'Please provide a link')
        elif resource_type == 'note' and not content:
            self.add_error('content', 'Please provide note content')
        
        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'content', 'is_shared']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

class VideoCallForm(forms.ModelForm):
    class Meta:
        model = VideoCall
        fields = ['max_participants']
        widgets = {
            'max_participants': forms.NumberInput(attrs={'min': 2, 'max': 50}),
        }

class ScreenShareForm(forms.ModelForm):
    class Meta:
        model = ScreenShare
        fields = []  # No fields needed for screen sharing form

class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ['title', 'description', 'scheduled_start', 'scheduled_end', 'has_video_call', 'has_screen_sharing', 'has_document_collaboration']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'scheduled_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'scheduled_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        scheduled_start = cleaned_data.get('scheduled_start')
        scheduled_end = cleaned_data.get('scheduled_end')
        
        if scheduled_start and scheduled_end:
            now = timezone.now()
            next_year = now + timedelta(days=365)
            
            # Check if start time is in the past
            if scheduled_start < now:
                self.add_error('scheduled_start', 'Start time cannot be in the past')
            
            # Check if end time is beyond next year
            if scheduled_end > next_year:
                self.add_error('scheduled_end', 'Session cannot be scheduled beyond next year')
            
            # Check if end time is before start time
            if scheduled_end <= scheduled_start:
                self.add_error('scheduled_end', 'End time must be after start time')
            
            # Check if duration is more than 1 hour
            duration = scheduled_end - scheduled_start
            if duration > timedelta(hours=1):
                self.add_error('scheduled_end', 'Session duration cannot exceed 1 hour. Please create multiple sessions for longer durations.')
        
        return cleaned_data