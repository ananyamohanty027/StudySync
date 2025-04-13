from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import StudyRoom, Participant, SharedResource, Document, ChatMessage, DocumentEdit

def create_user_groups():
    # Create Study Platform User group
    study_platform_group, created = Group.objects.get_or_create(name='Study Platform User')
    
    # Get content types
    study_room_ct = ContentType.objects.get_for_model(StudyRoom)
    participant_ct = ContentType.objects.get_for_model(Participant)
    shared_resource_ct = ContentType.objects.get_for_model(SharedResource)
    document_ct = ContentType.objects.get_for_model(Document)
    chat_message_ct = ContentType.objects.get_for_model(ChatMessage)
    document_edit_ct = ContentType.objects.get_for_model(DocumentEdit)

    # Define permissions for Study Platform User
    study_room_permissions = [
        'view_studyroom',
        'add_studyroom',
        'change_studyroom',
        'delete_studyroom',
    ]

    participant_permissions = [
        'view_participant',
        'add_participant',
        'change_participant',
        'delete_participant',
    ]

    shared_resource_permissions = [
        'view_sharedresource',
        'add_sharedresource',
        'change_sharedresource',
        'delete_sharedresource',
    ]

    document_permissions = [
        'view_document',
        'add_document',
        'change_document',
        'delete_document',
    ]

    chat_message_permissions = [
        'view_chatmessage',
        'add_chatmessage',
        'change_chatmessage',
        'delete_chatmessage',
    ]

    document_edit_permissions = [
        'view_documentedit',
        'add_documentedit',
        'change_documentedit',
        'delete_documentedit',
    ]

    # Add permissions to group
    for perm_name in study_room_permissions:
        perm = Permission.objects.get(content_type=study_room_ct, codename=perm_name)
        study_platform_group.permissions.add(perm)

    for perm_name in participant_permissions:
        perm = Permission.objects.get(content_type=participant_ct, codename=perm_name)
        study_platform_group.permissions.add(perm)

    for perm_name in shared_resource_permissions:
        perm = Permission.objects.get(content_type=shared_resource_ct, codename=perm_name)
        study_platform_group.permissions.add(perm)

    for perm_name in document_permissions:
        perm = Permission.objects.get(content_type=document_ct, codename=perm_name)
        study_platform_group.permissions.add(perm)

    for perm_name in chat_message_permissions:
        perm = Permission.objects.get(content_type=chat_message_ct, codename=perm_name)
        study_platform_group.permissions.add(perm)

    for perm_name in document_edit_permissions:
        perm = Permission.objects.get(content_type=document_edit_ct, codename=perm_name)
        study_platform_group.permissions.add(perm)

    return study_platform_group

def assign_user_permissions(user):
    """Assign default permissions to a new user"""
    study_platform_group = Group.objects.get(name='Study Platform User')
    user.groups.add(study_platform_group) 