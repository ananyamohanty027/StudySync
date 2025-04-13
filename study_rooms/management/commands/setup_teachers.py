from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from study_rooms.models import Teacher, StudyRoom

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up initial teacher IDs and cleans up existing rooms'

    def handle(self, *args, **kwargs):
        # Clean up existing rooms
        StudyRoom.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all existing rooms'))

        # Create teacher IDs
        teacher_ids = ['101', '102', '103']
        
        for teacher_id in teacher_ids:
            # Check if teacher ID already exists
            if not Teacher.objects.filter(teacher_id=teacher_id).exists():
                # Create a user for the teacher if it doesn't exist
                username = f'teacher{teacher_id}'
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@example.com',
                        'is_staff': True
                    }
                )
                if created:
                    user.set_password(f'teacher{teacher_id}')  # Default password
                    user.save()
                
                # Create the teacher
                Teacher.objects.create(
                    user=user,
                    teacher_id=teacher_id,
                    is_verified=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created teacher with ID: {teacher_id}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Teacher ID {teacher_id} already exists')
                )
