"""
Django management command to send deadline reminders.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.email_service import NotificationService


class Command(BaseCommand):
    help = 'Send deadline reminder notifications for scholarships closing soon'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=3,
            help='Number of days before deadline to send reminder (default: 3)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending notifications'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'Looking for scholarships closing in {days} days...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No notifications will be sent')
            )
        
        # Send deadline reminders
        if not dry_run:
            notifications_sent = NotificationService.send_deadline_reminders()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent {notifications_sent} deadline reminder notifications'
                )
            )
        else:
            from datetime import timedelta
            from core.models import Scholarship
            
            # Find scholarships closing soon
            reminder_date = timezone.now() + timedelta(days=days)
            scholarships_closing = Scholarship.objects.filter(
                is_active=True,
                application_deadline__lte=reminder_date,
                application_deadline__gt=timezone.now()
            )
            
            if scholarships_closing.exists():
                self.stdout.write(
                    self.style.SUCCESS(f'Found {scholarships_closing.count()} scholarships closing soon:')
                )
                
                for scholarship in scholarships_closing:
                    days_left = (scholarship.application_deadline - timezone.now()).days
                    self.stdout.write(f'  - {scholarship.title} (closes in {days_left} days)')
            else:
                self.stdout.write(
                    self.style.WARNING('No scholarships found closing in the specified time period')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Deadline reminder command completed successfully')
        )