"""
Business logic services for the Scholarship Management System.

This module contains service classes that encapsulate business logic
for scholarships, applications, and notifications.
"""

from django.utils import timezone
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum, Avg, F
from datetime import timedelta
from typing import List, Dict, Optional, Tuple

from .models import Scholarship, Application, Notification, UserProfile


class ScholarshipService:
    """Service class for scholarship-related business logic."""
    
    @staticmethod
    def create_scholarship(created_by: User, **data) -> Scholarship:
        """Create a new scholarship with validation."""
        if not created_by.profile.is_admin:
            raise ValidationError("Only administrators can create scholarships.")
        
        # Validate application deadline
        application_deadline = data.get('application_deadline')
        if application_deadline and application_deadline <= timezone.now():
            raise ValidationError("Application deadline must be in the future.")
        
        # Validate award date
        award_date = data.get('award_date')
        if award_date and application_deadline and award_date <= application_deadline:
            raise ValidationError("Award date must be after application deadline.")
        
        # Create scholarship
        scholarship = Scholarship.objects.create(
            created_by=created_by,
            **data
        )
        
        # Create notification for all students
        NotificationService.notify_all_students(
            title="New Scholarship Available!",
            message=f"A new scholarship '{scholarship.title}' is now available for applications.",
            notification_type='info'
        )
        
        return scholarship
    
    @staticmethod
    def update_scholarship(scholarship: Scholarship, updated_by: User, **data) -> Scholarship:
        """Update an existing scholarship with validation."""
        if not updated_by.profile.is_admin:
            raise ValidationError("Only administrators can update scholarships.")
        
        if scholarship.created_by != updated_by:
            raise ValidationError("You can only update scholarships you created.")
        
        # Check if scholarship has applications
        has_applications = scholarship.applications.exists()
        
        # Prevent critical changes if applications exist
        if has_applications:
            critical_fields = ['amount', 'total_slots', 'application_deadline']
            for field in critical_fields:
                if field in data and getattr(scholarship, field) != data[field]:
                    raise ValidationError(
                        f"Cannot modify {field} - scholarship already has applications."
                    )
        
        # Update scholarship
        for key, value in data.items():
            setattr(scholarship, key, value)
        
        scholarship.updated_at = timezone.now()
        scholarship.save()
        
        return scholarship
    
    @staticmethod
    def deactivate_scholarship(scholarship: Scholarship, deactivated_by: User) -> Scholarship:
        """Deactivate a scholarship."""
        if not deactivated_by.profile.is_admin:
            raise ValidationError("Only administrators can deactivate scholarships.")
        
        if scholarship.created_by != deactivated_by:
            raise ValidationError("You can only deactivate scholarships you created.")
        
        scholarship.is_active = False
        scholarship.save()
        
        # Notify students with pending applications
        pending_applications = scholarship.applications.filter(status='pending')
        for application in pending_applications:
            NotificationService.create_notification(
                recipient=application.user,
                title="Scholarship Deactivated",
                message=f"The scholarship '{scholarship.title}' you applied for has been deactivated.",
                notification_type='warning',
                related_application=application
            )
        
        return scholarship
    
    @staticmethod
    def get_available_scholarships(for_user: Optional[User] = None) -> List[Scholarship]:
        """Get scholarships available for application."""
        scholarships = Scholarship.objects.filter(
            is_active=True,
            application_deadline__gt=timezone.now()
        ).annotate(
            applications_count=Count('applications')
        ).filter(
            applications_count__lt=F('total_slots')
        )
        
        if for_user and for_user.profile.is_student:
            # Exclude scholarships user already applied to
            applied_scholarship_ids = Application.objects.filter(
                user=for_user
            ).values_list('scholarship_id', flat=True)
            scholarships = scholarships.exclude(id__in=applied_scholarship_ids)
        
        return scholarships.order_by('application_deadline')
    
    @staticmethod
    def get_scholarship_analytics(scholarship: Scholarship) -> Dict:
        """Get analytics data for a scholarship."""
        applications = scholarship.applications.all()
        
        return {
            'total_applications': applications.count(),
            'pending_applications': applications.filter(status='pending').count(),
            'approved_applications': applications.filter(status='approved').count(),
            'rejected_applications': applications.filter(status='rejected').count(),
            'under_review_applications': applications.filter(status='under_review').count(),
            'additional_info_applications': applications.filter(status='additional_info_required').count(),
            'available_slots': scholarship.available_slots_remaining,
            'completion_rate': scholarship.completion_percentage,
            'days_until_deadline': (scholarship.application_deadline - timezone.now()).days if scholarship.application_deadline > timezone.now() else 0,
        }


class ApplicationService:
    """Service class for application-related business logic."""
    
    @staticmethod
    @transaction.atomic
    def submit_application(user: User, scholarship: Scholarship, **application_data) -> Application:
        """Submit a new scholarship application."""
        if not user.profile.is_student:
            raise ValidationError("Only students can apply for scholarships.")
        
        # Check if scholarship is available
        if not scholarship.is_active:
            raise ValidationError("This scholarship is no longer available.")
        
        if scholarship.application_deadline <= timezone.now():
            raise ValidationError("Application deadline has passed.")
        
        if scholarship.available_slots_remaining <= 0:
            raise ValidationError("No more slots available for this scholarship.")
        
        # Check if user already applied
        existing_application = Application.objects.filter(
            user=user,
            scholarship=scholarship
        ).first()
        
        if existing_application:
            raise ValidationError("You have already applied for this scholarship.")
        
        # Create application
        application = Application.objects.create(
            user=user,
            scholarship=scholarship,
            **application_data
        )
        
        # Notify administrators
        admin_users = User.objects.filter(profile__user_type='admin')
        for admin in admin_users:
            NotificationService.create_notification(
                recipient=admin,
                title="New Application Received",
                message=f"New application from {user.get_full_name()} for {scholarship.title}",
                notification_type='info',
                related_application=application
            )
        
        return application
    
    @staticmethod
    @transaction.atomic
    def assign_application(application: Application, reviewer: User) -> Application:
        """Assign an application to a reviewer."""
        if not reviewer.profile.is_osas:
            raise ValidationError("Only OSAS staff can be assigned to review applications.")
        
        if application.status != 'pending':
            raise ValidationError("Only pending applications can be assigned.")
        
        application.reviewer = reviewer
        application.status = 'under_review'
        application.save()
        
        # Notify student
        NotificationService.create_notification(
            recipient=application.user,
            title="Application Under Review",
            message=f"Your application for {application.scholarship.title} is now under review.",
            notification_type='info',
            related_application=application
        )
        
        return application
    
    @staticmethod
    @transaction.atomic
    def process_review_decision(
        application: Application,
        reviewer: User,
        decision: str,
        comments: str = ""
    ) -> Application:
        """Process a review decision for an application."""
        if not reviewer.profile.is_osas:
            raise ValidationError("Only OSAS staff can review applications.")
        
        if application.status not in ['pending', 'under_review', 'additional_info_required']:
            raise ValidationError("This application has already been reviewed.")
        
        valid_decisions = ['approved', 'rejected', 'additional_info_required']
        if decision not in valid_decisions:
            raise ValidationError(f"Invalid decision. Must be one of: {valid_decisions}")
        
        # Check available slots for approval
        if decision == 'approved' and application.scholarship.available_slots_remaining <= 0:
            raise ValidationError("No more slots available for this scholarship.")
        
        # Update application
        application.status = decision
        application.reviewer = reviewer
        application.review_comments = comments
        application.reviewed_at = timezone.now()
        application.save()
        
        # Create appropriate notification
        if decision == 'approved':
            title = "Scholarship Application Approved!"
            message = f"Congratulations! Your application for {application.scholarship.title} has been approved."
            notification_type = 'success'
        elif decision == 'rejected':
            title = "Scholarship Application Update"
            message = f"Your application for {application.scholarship.title} has been reviewed."
            notification_type = 'info'
        else:  # additional_info_required
            title = "Additional Information Required"
            message = f"Please provide additional information for your {application.scholarship.title} application."
            notification_type = 'warning'
        
        NotificationService.create_notification(
            recipient=application.user,
            title=title,
            message=message,
            notification_type=notification_type,
            related_application=application
        )
        
        return application
    
    @staticmethod
    def get_application_analytics(user: User) -> Dict:
        """Get application analytics for a user."""
        if user.profile.is_student:
            applications = Application.objects.filter(user=user)
        elif user.profile.is_admin:
            applications = Application.objects.filter(scholarship__created_by=user)
        elif user.profile.is_osas:
            applications = Application.objects.all()
        else:
            applications = Application.objects.none()
        
        total_count = applications.count()
        
        if total_count == 0:
            return {
                'total_applications': 0,
                'pending': 0,
                'under_review': 0,
                'approved': 0,
                'rejected': 0,
                'additional_info_required': 0,
                'success_rate': 0.0,
            }
        
        status_counts = applications.values('status').annotate(count=Count('id'))
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        approved_count = status_dict.get('approved', 0)
        success_rate = (approved_count / total_count) * 100 if total_count > 0 else 0
        
        return {
            'total_applications': total_count,
            'pending': status_dict.get('pending', 0),
            'under_review': status_dict.get('under_review', 0),
            'approved': approved_count,
            'rejected': status_dict.get('rejected', 0),
            'additional_info_required': status_dict.get('additional_info_required', 0),
            'success_rate': round(success_rate, 1),
        }
    
    @staticmethod
    def get_priority_applications(limit: int = 10) -> List[Application]:
        """Get priority applications that need immediate attention."""
        # Priority logic: 
        # 1. Applications close to scholarship deadline
        # 2. Applications pending for longest time
        # 3. High-value scholarships
        
        now = timezone.now()
        priority_applications = Application.objects.filter(
            status='pending'
        ).select_related('scholarship', 'user').annotate(
            days_to_deadline=F('scholarship__application_deadline') - now,
            days_pending=now - F('created_at')
        ).order_by(
            'days_to_deadline',  # Closest deadline first
            '-days_pending',     # Longest pending first
            '-scholarship__amount'  # Higher value first
        )[:limit]
        
        return list(priority_applications)


class NotificationService:
    """Service class for notification-related business logic."""
    
    @staticmethod
    def create_notification(
        recipient: User,
        title: str,
        message: str,
        notification_type: str = 'info',
        related_application: Optional[Application] = None
    ) -> Notification:
        """Create a new notification."""
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            related_application=related_application
        )
        return notification
    
    @staticmethod
    def notify_all_students(
        title: str,
        message: str,
        notification_type: str = 'info'
    ) -> List[Notification]:
        """Send notification to all active students."""
        students = User.objects.filter(
            profile__user_type='student',
            is_active=True
        )
        
        notifications = []
        for student in students:
            notification = NotificationService.create_notification(
                recipient=student,
                title=title,
                message=message,
                notification_type=notification_type
            )
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def mark_as_read(notification: Notification, user: User) -> Notification:
        """Mark a notification as read."""
        if notification.recipient != user:
            raise ValidationError("You can only mark your own notifications as read.")
        
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return notification
    
    @staticmethod
    def get_unread_notifications(user: User, limit: int = 10) -> List[Notification]:
        """Get unread notifications for a user."""
        return list(
            Notification.objects.filter(
                recipient=user,
                is_read=False
            ).order_by('-created_at')[:limit]
        )
    
    @staticmethod
    def cleanup_old_notifications(days: int = 30) -> int:
        """Clean up old read notifications."""
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count = Notification.objects.filter(
            is_read=True,
            read_at__lt=cutoff_date
        ).delete()[0]
        
        return deleted_count
    
    @staticmethod
    def send_deadline_reminders() -> List[Notification]:
        """Send deadline reminders for scholarships closing soon."""
        # Find scholarships closing in the next 3 days
        reminder_date = timezone.now() + timedelta(days=3)
        scholarships_closing = Scholarship.objects.filter(
            is_active=True,
            application_deadline__lte=reminder_date,
            application_deadline__gt=timezone.now()
        )
        
        notifications = []
        
        for scholarship in scholarships_closing:
            # Get students who haven't applied yet
            applied_users = scholarship.applications.values_list('user_id', flat=True)
            students_to_notify = User.objects.filter(
                profile__user_type='student',
                is_active=True
            ).exclude(id__in=applied_users)
            
            days_left = (scholarship.application_deadline - timezone.now()).days
            
            for student in students_to_notify:
                notification = NotificationService.create_notification(
                    recipient=student,
                    title="Scholarship Deadline Reminder",
                    message=f"Only {days_left} days left to apply for {scholarship.title}!",
                    notification_type='warning'
                )
                notifications.append(notification)
        
        return notifications


class AnalyticsService:
    """Service class for system analytics and reporting."""
    
    @staticmethod
    def get_system_overview() -> Dict:
        """Get system-wide analytics overview."""
        now = timezone.now()
        
        return {
            'total_users': User.objects.filter(is_active=True).count(),
            'total_students': User.objects.filter(profile__user_type='student', is_active=True).count(),
            'total_admins': User.objects.filter(profile__user_type='admin', is_active=True).count(),
            'total_osas': User.objects.filter(profile__user_type='osas', is_active=True).count(),
            'total_scholarships': Scholarship.objects.count(),
            'active_scholarships': Scholarship.objects.filter(is_active=True).count(),
            'total_applications': Application.objects.count(),
            'pending_applications': Application.objects.filter(status='pending').count(),
            'approved_applications': Application.objects.filter(status='approved').count(),
            'total_notifications': Notification.objects.count(),
            'unread_notifications': Notification.objects.filter(is_read=False).count(),
        }
    
    @staticmethod
    def get_scholarship_performance_report() -> List[Dict]:
        """Get performance report for all scholarships."""
        scholarships = Scholarship.objects.annotate(
            total_applications=Count('applications'),
            approved_applications=Count('applications', filter=Q(applications__status='approved')),
            pending_applications=Count('applications', filter=Q(applications__status='pending'))
        ).order_by('-total_applications')
        
        report = []
        for scholarship in scholarships:
            success_rate = 0
            if scholarship.total_applications > 0:
                success_rate = (scholarship.approved_applications / scholarship.total_applications) * 100
            
            report.append({
                'scholarship': scholarship,
                'total_applications': scholarship.total_applications,
                'approved_applications': scholarship.approved_applications,
                'pending_applications': scholarship.pending_applications,
                'success_rate': round(success_rate, 1),
                'available_slots': scholarship.available_slots_remaining,
                'completion_rate': scholarship.completion_percentage,
            })
        
        return report
    
    @staticmethod
    def get_user_activity_report(days: int = 30) -> Dict:
        """Get user activity report for the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        return {
            'new_users': User.objects.filter(date_joined__gte=cutoff_date).count(),
            'new_applications': Application.objects.filter(created_at__gte=cutoff_date).count(),
            'new_scholarships': Scholarship.objects.filter(created_at__gte=cutoff_date).count(),
            'processed_applications': Application.objects.filter(
                reviewed_at__gte=cutoff_date
            ).exclude(status__in=['pending', 'under_review']).count(),
            'active_users': User.objects.filter(
                last_login__gte=cutoff_date,
                is_active=True
            ).count(),
        }