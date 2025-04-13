from django.core.management.base import BaseCommand
from study_rooms.permissions import create_user_groups

class Command(BaseCommand):
    help = 'Sets up the Study Platform User group with all necessary permissions'

    def handle(self, *args, **options):
        self.stdout.write('Creating Study Platform User group and permissions...')
        group = create_user_groups()
        self.stdout.write(self.style.SUCCESS(f'Successfully created group: {group.name}'))
        self.stdout.write('All permissions have been set up successfully!') 