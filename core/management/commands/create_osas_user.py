"""
Management command to create OSAS staff user.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Create OSAS staff user for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='osas_staff',
            help='Username for OSAS user (default: osas_staff)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='osas123',
            help='Password for OSAS user (default: osas123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='osas@example.com',
            help='Email for OSAS user (default: osas@example.com)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.WARNING('Creating OSAS Staff User'))
        self.stdout.write('=' * 60)
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists'))
            
            # Update profile to ensure it's OSAS
            profile, created = UserProfile.objects.get_or_create(user=user)
            if profile.user_type != 'osas':
                profile.user_type = 'osas'
                profile.save()
                self.stdout.write(self.style.SUCCESS('Updated user type to OSAS'))
            else:
                self.stdout.write('User is already OSAS staff')
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='OSAS',
                last_name='Staff'
            )
            self.stdout.write(self.style.SUCCESS(f'✓ Created user: {username}'))
            
            # Ensure profile exists and set type to OSAS
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.user_type = 'osas'
            profile.save()
            self.stdout.write(self.style.SUCCESS('✓ Set user type to OSAS'))
        
        # Verify setup
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('OSAS User Details:'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'Username:     {user.username}')
        self.stdout.write(f'Email:        {user.email}')
        self.stdout.write(f'Password:     {password}')
        self.stdout.write(f'User Type:    {user.profile.user_type}')
        self.stdout.write(f'Is OSAS:      {user.profile.is_osas}')
        self.stdout.write(f'Is Admin:     {user.profile.is_admin}')
        self.stdout.write(f'Is Student:   {user.profile.is_student}')
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('Login Instructions:'))
        self.stdout.write('=' * 60)
        self.stdout.write('1. Go to: http://localhost:8000/auth/login/')
        self.stdout.write(f'2. Username: {username}')
        self.stdout.write(f'3. Password: {password}')
        self.stdout.write('4. Should redirect to: /osas/ (OSAS Dashboard)')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ OSAS user ready!'))
        self.stdout.write('=' * 60)
