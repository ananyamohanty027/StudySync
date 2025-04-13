from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import StudyRoom, Participant, SharedResource, ChatMessage, Document, DocumentEdit, User, VideoCall, ScreenShare, StudySession, Teacher
from .forms import StudyRoomForm, ResourceForm, DocumentForm, VideoCallForm, ScreenShareForm, StudySessionForm

def is_teacher(user):
    return hasattr(user, 'teacher') and user.teacher.is_verified

def home(request):
    """Home page view"""
    print("\n=== HOME VIEW CALLED ===")
    print(f"Request path: {request.path}")
    print(f"Template being rendered: study_rooms/home.html")
    return render(request, 'study_rooms/home.html')

@login_required
def room_list(request):
    # Debug information about the user
    print("\n=== DEBUG INFORMATION ===")
    print(f"Current user: {request.user.username}")
    print(f"User is authenticated: {request.user.is_authenticated}")
    print(f"User ID: {request.user.id}")
    
    # Get all rooms where the user is either a participant or the host
    user_rooms = StudyRoom.objects.filter(
        models.Q(participants__user=request.user) | models.Q(host=request.user)
    ).distinct().order_by('-created_at')
    
    # Get all rooms created by the user
    created_rooms = StudyRoom.objects.filter(host=request.user).order_by('-created_at')
    
    # Get all public rooms that the user is not already a participant in and not the host
    public_rooms = StudyRoom.objects.filter(
        is_private=False
    ).exclude(
        models.Q(participants__user=request.user) | models.Q(host=request.user)
    ).distinct().order_by('-created_at')
    
    # Debug information
    print("\n=== ROOM COUNTS ===")
    print(f"User rooms count: {user_rooms.count()}")
    print(f"Created rooms count: {created_rooms.count()}")
    print(f"Public rooms count: {public_rooms.count()}")
    
    # Print all created rooms
    print("\n=== CREATED ROOMS ===")
    for room in created_rooms:
        print(f"- {room.name} (ID: {room.id}, Host: {room.host.username})")
    
    # Print all user rooms
    print("\n=== USER ROOMS ===")
    for room in user_rooms:
        print(f"- {room.name} (ID: {room.id}, Host: {room.host.username})")
    
    # Print all public rooms
    print("\n=== PUBLIC ROOMS ===")
    for room in public_rooms:
        print(f"- {room.name} (ID: {room.id}, Host: {room.host.username})")
    
    print("\n=== END DEBUG ===\n")
    
    return render(request, 'study_rooms/room_list_simple.html', {
        'public_rooms': public_rooms,
        'user_rooms': user_rooms,
        'created_rooms': created_rooms,
        'debug': True  # Enable debug information in template
    })

@login_required
def create_room(request):
    if not is_teacher(request.user):
        messages.error(request, 'Only verified teachers can create study rooms. Please enter your teacher ID to get verified.')
        return redirect('study_rooms:verify_teacher')
        
    if request.method == 'POST':
        form = StudyRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            Participant.objects.create(user=request.user, room=room, is_moderator=True)
            messages.success(request, 'Study room created successfully!')
            return redirect('study_rooms:room_detail', pk=room.pk)
    else:
        form = StudyRoomForm()
    return render(request, 'study_rooms/create_room.html', {'form': form})

@login_required
def verify_teacher(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        try:
            # Check if this is a valid teacher ID
            teacher = Teacher.objects.get(teacher_id=teacher_id)
            if teacher.user != request.user:
                # If the ID exists but belongs to another user
                if Teacher.objects.filter(user=request.user).exists():
                    messages.error(request, 'You are already associated with a different teacher ID.')
                else:
                    messages.error(request, 'This teacher ID is already associated with another user.')
            else:
                teacher.is_verified = True
                teacher.save()
                messages.success(request, 'Teacher verification successful! You can now create study rooms.')
                return redirect('study_rooms:create_room')
        except Teacher.DoesNotExist:
            if Teacher.objects.filter(user=request.user).exists():
                messages.error(request, 'You are already associated with a different teacher ID.')
            else:
                # Create new teacher record
                Teacher.objects.create(
                    user=request.user,
                    teacher_id=teacher_id,
                    is_verified=False
                )
                messages.info(request, 'Teacher ID submitted for verification. Please wait for admin approval.')
    
    return render(request, 'study_rooms/verify_teacher.html')

@login_required
def room_detail(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    is_participant = room.participants.filter(user=request.user).exists()
    is_moderator = room.participants.filter(user=request.user, is_moderator=True).exists() if is_participant else False
    
    if room.is_private and not is_participant:
        messages.error(request, 'This is a private room. You need to be invited to join.')
        return redirect('study_rooms:room_list')
    
    resources = room.resources.all().order_by('-shared_at')
    chat_messages = room.messages.all().order_by('-timestamp')[:50]
    documents = room.documents.filter(is_shared=True).order_by('-last_modified')
    active_video_call = room.video_calls.filter(is_active=True).first()
    active_screen_share = room.screen_shares.filter(is_active=True).first()
    study_sessions = room.study_sessions.filter(is_active=True).order_by('scheduled_start')
    
    # Debug information
    print(f"Room: {room.name}")
    print(f"Has video call: {room.has_video_call}")
    print(f"Has screen sharing: {room.has_screen_sharing}")
    print(f"Active video call: {active_video_call}")
    print(f"Active screen share: {active_screen_share}")
    
    return render(request, 'study_rooms/room_detail.html', {
        'room': room,
        'is_participant': is_participant,
        'is_moderator': is_moderator,
        'resources': resources,
        'chat_messages': chat_messages,
        'documents': documents,
        'active_video_call': active_video_call,
        'active_screen_share': active_screen_share,
        'study_sessions': study_sessions
    })

@login_required
@require_POST
def join_room(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    
    if room.participants.count() >= room.max_participants:
        messages.error(request, 'This room is full.')
        return redirect('study_rooms:room_list')
    
    if room.is_private:
        password = request.POST.get('password')
        if not password or password != room.password:
            messages.error(request, 'Invalid password for private room.')
            return redirect('study_rooms:room_list')
    
    Participant.objects.get_or_create(user=request.user, room=room)
    messages.success(request, f'Welcome to {room.name}!')
    return redirect('study_rooms:room_detail', pk=room.pk)

@login_required
@require_POST
def leave_room(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    Participant.objects.filter(user=request.user, room=room).delete()
    messages.success(request, f'You have left {room.name}.')
    return redirect('study_rooms:room_list')

@login_required
def share_resource(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.room = room
            resource.shared_by = request.user
            resource.save()
            messages.success(request, 'Resource shared successfully!')
            return redirect('study_rooms:room_detail', pk=pk)
    else:
        form = ResourceForm()
    return render(request, 'study_rooms/share_resource.html', {
        'form': form,
        'room': room
    })

@login_required
@require_POST
def send_message(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    message = request.POST.get('message', '').strip()
    
    if not message:
        return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'})
    
    if not room.participants.filter(user=request.user).exists():
        return JsonResponse({'status': 'error', 'message': 'You must be a participant to send messages'})
    
    chat_message = ChatMessage.objects.create(
        room=room,
        user=request.user,
        message=message
    )
    
    return JsonResponse({
        'status': 'success',
        'message': {
            'id': chat_message.id,
            'text': chat_message.message,
            'username': chat_message.user.username,
            'timestamp': chat_message.timestamp.isoformat()
        }
    })

@login_required
def create_document(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.room = room
            document.created_by = request.user
            document.save()
            messages.success(request, 'Document created successfully!')
            return redirect('study_rooms:document_detail', pk=document.pk)
    else:
        form = DocumentForm()
    return render(request, 'study_rooms/create_document.html', {
        'form': form,
        'room': room
    })

@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.is_shared and document.created_by != request.user:
        messages.error(request, 'You do not have permission to view this document.')
        return redirect('study_rooms:room_detail', pk=document.room.pk)
    
    return render(request, 'study_rooms/document_detail.html', {
        'document': document
    })

@login_required
@require_POST
def save_document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'status': 'error', 'message': 'Content cannot be empty'})
    
    if not document.is_shared and document.created_by != request.user:
        return JsonResponse({'status': 'error', 'message': 'You do not have permission to edit this document'})
    
    document.content = content
    document.save()
    
    DocumentEdit.objects.create(
        document=document,
        user=request.user,
        content=content
    )
    
    return JsonResponse({'status': 'success'})

@login_required
def start_video_call(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    
    if not room.has_video_call:
        messages.error(request, 'Video calls are not enabled for this room.')
        return redirect('study_rooms:room_detail', pk=pk)
    
    active_call = room.video_calls.filter(is_active=True).first()
    if active_call:
        messages.info(request, 'A video call is already active in this room.')
        return redirect('study_rooms:room_detail', pk=pk)
    
    if request.method == 'POST':
        form = VideoCallForm(request.POST)
        if form.is_valid():
            video_call = form.save(commit=False)
            video_call.room = room
            video_call.started_by = request.user
            video_call.save()
            messages.success(request, 'Video call started successfully!')
            return redirect('study_rooms:room_detail', pk=pk)
    else:
        form = VideoCallForm()
    
    return render(request, 'study_rooms/start_video_call.html', {
        'form': form,
        'room': room
    })

@login_required
@require_POST
def end_video_call(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    video_call = room.video_calls.filter(is_active=True).first()
    
    if not video_call:
        messages.error(request, 'No active video call found.')
        return redirect('study_rooms:room_detail', pk=pk)
    
    if video_call.started_by != request.user and not room.participants.filter(user=request.user, is_moderator=True).exists():
        messages.error(request, 'You do not have permission to end this video call.')
        return redirect('study_rooms:room_detail', pk=pk)
    
    video_call.is_active = False
    video_call.ended_at = timezone.now()
    video_call.save()
    
    messages.success(request, 'Video call ended successfully!')
    return redirect('study_rooms:room_detail', pk=pk)

@login_required
def start_screen_share(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    
    if not room.has_screen_sharing:
        messages.error(request, 'Screen sharing is not enabled for this room.')
        return redirect('study_rooms:room_detail', pk=pk)
    
    active_share = room.screen_shares.filter(is_active=True).first()
    if active_share:
        messages.info(request, 'Someone is already sharing their screen in this room.')
        return redirect('study_rooms:room_detail', pk=pk)
    
    if request.method == 'POST':
        form = ScreenShareForm(request.POST)
        if form.is_valid():
            screen_share = form.save(commit=False)
            screen_share.room = room
            screen_share.shared_by = request.user
            screen_share.save()
            
            # Update participant status
            participant = room.participants.get(user=request.user)
            participant.is_screen_sharing = True
            participant.save()
            
            messages.success(request, 'Screen sharing started successfully!')
            return redirect('study_rooms:room_detail', pk=pk)
    else:
        form = ScreenShareForm()
    
    return render(request, 'study_rooms/start_screen_share.html', {
        'form': form,
        'room': room
    })

@login_required
@require_POST
def end_screen_share(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    screen_share = room.screen_shares.filter(is_active=True).first()
    
    if not screen_share:
        messages.error(request, 'No active screen share found.')
        return redirect('study_rooms:room_detail', pk=pk)
    
    if screen_share.shared_by != request.user and not room.participants.filter(user=request.user, is_moderator=True).exists():
        messages.error(request, 'You do not have permission to end this screen share.')
        return redirect('study_rooms:room_detail', pk=pk)
    
    screen_share.is_active = False
    screen_share.ended_at = timezone.now()
    screen_share.save()
    
    # Update participant status
    participant = room.participants.get(user=screen_share.shared_by)
    participant.is_screen_sharing = False
    participant.save()
    
    messages.success(request, 'Screen sharing ended successfully!')
    return redirect('study_rooms:room_detail', pk=pk)

@login_required
def create_study_session(request, pk):
    room = get_object_or_404(StudyRoom, pk=pk)
    
    if request.method == 'POST':
        form = StudySessionForm(request.POST)
        if form.is_valid():
            study_session = form.save(commit=False)
            study_session.room = room
            study_session.created_by = request.user
            study_session.save()
            messages.success(request, 'Study session scheduled successfully!')
            return redirect('study_rooms:room_detail', pk=pk)
    else:
        form = StudySessionForm()
    
    return render(request, 'study_rooms/create_study_session.html', {
        'form': form,
        'room': room
    })

@login_required
def study_session_detail(request, pk):
    study_session = get_object_or_404(StudySession, pk=pk)
    room = study_session.room
    
    if not room.participants.filter(user=request.user).exists() and room.host != request.user:
        messages.error(request, 'You do not have permission to view this study session.')
        return redirect('study_rooms:room_detail', pk=room.pk)
    
    return render(request, 'study_rooms/study_session_detail.html', {
        'study_session': study_session,
        'room': room,
        'username': request.user.username
    })

@login_required
def end_study_session(request, pk):
    study_session = get_object_or_404(StudySession, pk=pk)
    room = study_session.room
    
    # Check if user has permission
    if not room.participants.filter(user=request.user).exists() and room.host != request.user:
        messages.error(request, 'You do not have permission to end this study session.')
        return redirect('study_rooms:room_detail', pk=room.pk)
    
    # End the study session
    study_session.is_active = False
    study_session.save()
    
    # Notify all participants through WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'video_call_{pk}',
        {
            'type': 'session_ended',
            'message': 'Study session has ended.'
        }
    )
    
    messages.success(request, 'Study session has ended.')
    return redirect('study_rooms:room_detail', pk=room.pk)

@login_required
def profile(request):
    user_rooms = StudyRoom.objects.filter(participants__user=request.user)
    hosted_rooms = StudyRoom.objects.filter(host=request.user)
    study_sessions = StudySession.objects.filter(created_by=request.user, is_active=True).order_by('scheduled_start')
    recent_activity = []  # TODO: Implement activity tracking
    
    context = {
        'user_rooms': user_rooms,
        'hosted_rooms': hosted_rooms,
        'study_sessions': study_sessions,
        'recent_activity': recent_activity,
    }
    return render(request, 'study_rooms/profile.html', context)

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, "Passwords don't match")
            return redirect('account_signup')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('account_signup')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('account_signup')
            
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('study_rooms:home')
        
    return render(request, 'registration/signup.html')

@login_required
def study_session_list(request):
    """List all study sessions that the user has access to"""
    # Get study sessions from rooms where the user is a participant or host
    study_sessions = StudySession.objects.filter(
        models.Q(room__participants__user=request.user) | models.Q(room__host=request.user)
    ).distinct().order_by('scheduled_start')
    
    return render(request, 'study_rooms/study_session_list.html', {
        'study_sessions': study_sessions
    })
