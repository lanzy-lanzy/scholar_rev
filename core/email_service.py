"""
Email and notification services for the Scholarship Management System.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from typing import List, Optional, Dict, Any
import logging

from .models import Notification, Application, Scholarship

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    @staticmethod
    def send_notification_email(
        recipient: User,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        notification_type: str = 'info'
    ) -> bool:
        """Send notification email to user."""
        try:
            # Create email content from template
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = strip_tags(html_content)
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f'Email sent successfully to {recipient.email}: {subject}')
            return True
            
        except Exception as e:
            logger.error(f'Failed to send email to {recipient.email}: {str(e)}')
            return False
    
    @staticmethod
    def send_application_notification(application: Application, notification_type: str) -> bool:
        """Send application-related notification email."""
        context = {
            'user': application.user,
            'application': application,
            'scholarship': application.scholarship,
            'site_name': 'Scholarship Management System',
        }
        
        if notification_type == 'application_submitted':
            subject = f'Application Submitted: {application.scholarship.title}'
            template = 'application_submitted'
            return EmailService.send_notification_email(
                recipient=application.user,
                subject=subject,
                template_name=template,
                context=context,
                notification_type='info'
            )
        
        elif notification_type == 'application_approved':
            subject = f'Scholarship Approved: {application.scholarship.title}'
            template = 'application_approved'
            return EmailService.send_notification_email(
                recipient=application.user,
                subject=subject,
                template_name=template,
                context=context,
                notification_type='success'
            )
        
        elif notification_type == 'application_rejected':
            subject = f'Application Update: {application.scholarship.title}'
            template = 'application_rejected'
            return EmailService.send_notification_email(
                recipient=application.user,
                subject=subject,
                template_name=template,
                context=context,
                notification_type='info'
            )
        
        elif notification_type == 'additional_info_required':
            subject = f'Additional Information Required: {application.scholarship.title}'
            template = 'additional_info_required'
            return EmailService.send_notification_email(
                recipient=application.user,
                subject=subject,
                template_name=template,
                context=context,
                notification_type='warning'
            )
        
        elif notification_type == 'application_under_review':
            subject = f'Application Under Review: {application.scholarship.title}'
            template = 'application_under_review'
            return EmailService.send_notification_email(
                recipient=application.user,
                subject=subject,
                template_name=template,
                context=context,
                notification_type='info'
            )
        
        return False
    
    @staticmethod
    def send_scholarship_notification(scholarship: Scholarship, notification_type: str, recipients: List[User] = None) -> int:
        \"\"\"Send scholarship-related notification emails.\"\"\"
        sent_count = 0
        
        context = {
            'scholarship': scholarship,
            'site_name': 'Scholarship Management System',
        }
        
        if notification_type == 'new_scholarship':
            subject = f'New Scholarship Available: {scholarship.title}'
            template = 'new_scholarship'
            
            # If no recipients specified, send to all active students
            if recipients is None:
                recipients = User.objects.filter(
                    profile__user_type='student',
                    is_active=True
                )
            
            for recipient in recipients:
                context['user'] = recipient
                if EmailService.send_notification_email(
                    recipient=recipient,
                    subject=subject,
                    template_name=template,
                    context=context,
                    notification_type='info'
                ):
                    sent_count += 1
        
        elif notification_type == 'deadline_reminder':
            subject = f'Deadline Reminder: {scholarship.title}'
            template = 'deadline_reminder'
            
            # Get students who haven't applied yet
            if recipients is None:
                applied_users = scholarship.applications.values_list('user_id', flat=True)
                recipients = User.objects.filter(
                    profile__user_type='student',
                    is_active=True
                ).exclude(id__in=applied_users)
            
            days_left = (scholarship.application_deadline - timezone.now()).days
            context['days_left'] = days_left
            
            for recipient in recipients:
                context['user'] = recipient
                if EmailService.send_notification_email(
                    recipient=recipient,
                    subject=subject,
                    template_name=template,
                    context=context,
                    notification_type='warning'
                ):
                    sent_count += 1
        
        return sent_count
    
    @staticmethod
    def send_admin_notification(scholarship: Scholarship, notification_type: str) -> bool:
        \"\"\"Send notifications to administrators.\"\"\"
        admin_users = User.objects.filter(profile__user_type='admin', is_active=True)
        
        context = {
            'scholarship': scholarship,
            'site_name': 'Scholarship Management System',
        }
        
        sent_count = 0
        
        if notification_type == 'new_application':
            # Get recent applications for this scholarship
            recent_applications = scholarship.applications.filter(
                submitted_at__gte=timezone.now() - timezone.timedelta(hours=1)
            ).count()
            
            subject = f'New Application(s) Received: {scholarship.title}'
            template = 'new_application_admin'
            context['recent_applications'] = recent_applications
            
            for admin in admin_users:
                context['user'] = admin
                if EmailService.send_notification_email(
                    recipient=admin,
                    subject=subject,
                    template_name=template,
                    context=context,
                    notification_type='info'
                ):
                    sent_count += 1
        
        return sent_count > 0


class NotificationService:
    \"\"\"Enhanced notification service with email integration.\"\"\"
    
    @staticmethod
    def create_notification(
        recipient: User,
        title: str,
        message: str,
        notification_type: str = 'info',
        related_application: Optional[Application] = None,
        send_email: bool = True
    ) -> Notification:
        \"\"\"Create a notification and optionally send email.\"\"\"
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            related_application=related_application
        )
        
        # Send email notification if enabled
        if send_email and hasattr(settings, 'EMAIL_BACKEND'):
            context = {
                'user': recipient,
                'notification': notification,
                'site_name': 'Scholarship Management System',
            }
            
            EmailService.send_notification_email(
                recipient=recipient,
                subject=title,
                template_name='generic_notification',
                context=context,
                notification_type=notification_type
            )
        
        return notification
    
    @staticmethod
    def notify_application_status_change(application: Application, old_status: str) -> None:
        \"\"\"Send notifications when application status changes.\"\"\"
        # Determine notification type based on status change
        if application.status == 'approved' and old_status != 'approved':
            NotificationService.create_notification(
                recipient=application.user,
                title='Scholarship Application Approved!',
                message=f'Congratulations! Your application for {application.scholarship.title} has been approved.',
                notification_type='success',
                related_application=application
            )
            EmailService.send_application_notification(application, 'application_approved')
        
        elif application.status == 'rejected' and old_status != 'rejected':
            NotificationService.create_notification(
                recipient=application.user,
                title='Scholarship Application Update',
                message=f'Your application for {application.scholarship.title} has been reviewed. Please check the details.',
                notification_type='info',
                related_application=application
            )
            EmailService.send_application_notification(application, 'application_rejected')
        
        elif application.status == 'additional_info_required' and old_status != 'additional_info_required':
            NotificationService.create_notification(
                recipient=application.user,
                title='Additional Information Required',
                message=f'Please provide additional information for your {application.scholarship.title} application.',
                notification_type='warning',
                related_application=application
            )
            EmailService.send_application_notification(application, 'additional_info_required')
        
        elif application.status == 'under_review' and old_status != 'under_review':
            NotificationService.create_notification(
                recipient=application.user,
                title='Application Under Review',
                message=f'Your application for {application.scholarship.title} is now under review.',
                notification_type='info',
                related_application=application
            )
            EmailService.send_application_notification(application, 'application_under_review')
    
    @staticmethod
    def notify_new_scholarship(scholarship: Scholarship) -> int:
        \"\"\"Notify all students about a new scholarship.\"\"\"
        students = User.objects.filter(
            profile__user_type='student',
            is_active=True
        )
        
        notification_count = 0
        
        for student in students:
            NotificationService.create_notification(
                recipient=student,
                title='New Scholarship Available!',
                message=f'A new scholarship \"{scholarship.title}\" is now available for applications.',
                notification_type='info',
                send_email=False  # Will send bulk email separately
            )
            notification_count += 1
        
        # Send bulk email notification
        EmailService.send_scholarship_notification(scholarship, 'new_scholarship')
        
        return notification_count
    
    @staticmethod
    def send_deadline_reminders() -> int:
        \"\"\"Send deadline reminders for scholarships closing soon.\"\"\"
        from datetime import timedelta
        
        # Find scholarships closing in the next 3 days
        reminder_date = timezone.now() + timedelta(days=3)
        scholarships_closing = Scholarship.objects.filter(
            is_active=True,
            application_deadline__lte=reminder_date,
            application_deadline__gt=timezone.now()
        )
        
        total_notifications = 0
        
        for scholarship in scholarships_closing:
            # Get students who haven't applied yet
            applied_users = scholarship.applications.values_list('user_id', flat=True)
            students_to_notify = User.objects.filter(
                profile__user_type='student',
                is_active=True
            ).exclude(id__in=applied_users)
            
            days_left = (scholarship.application_deadline - timezone.now()).days
            
            for student in students_to_notify:
                NotificationService.create_notification(
                    recipient=student,
                    title='Scholarship Deadline Reminder',
                    message=f'Only {days_left} day(s) left to apply for {scholarship.title}!',
                    notification_type='warning',
                    send_email=False  # Will send bulk email separately
                )
                total_notifications += 1
            
            # Send bulk email reminders
            EmailService.send_scholarship_notification(
                scholarship, 'deadline_reminder', students_to_notify
            )
        
        return total_notifications
    
    @staticmethod
    def mark_notifications_read(user: User, notification_ids: List[int] = None) -> int:
        \"\"\"Mark notifications as read for a user.\"\"\"
        notifications = Notification.objects.filter(
            recipient=user,
            is_read=False
        )
        
        if notification_ids:
            notifications = notifications.filter(id__in=notification_ids)
        
        updated_count = notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return updated_count
    
    @staticmethod
    def cleanup_old_notifications(days: int = 30) -> int:
        \"\"\"Clean up old read notifications.\"\"\"
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        deleted_count = Notification.objects.filter(
            is_read=True,
            created_at__lt=cutoff_date
        ).delete()[0]
        
        return deleted_count