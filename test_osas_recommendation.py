"""
Test script to simulate OSAS recommendation
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from core.models import Application, User, Notification
from django.utils import timezone

print("=" * 60)
print("SIMULATING OSAS RECOMMENDATION")
print("=" * 60)

# Get the application under review
under_review_app = Application.objects.filter(status='under_review').first()

if not under_review_app:
    print("\nNo applications under review found.")
    print("Please have an OSAS user assign an application to themselves first.")
    exit()

print(f"\nApplication found:")
print(f"  Student: {under_review_app.student.get_full_name()}")
print(f"  Scholarship: {under_review_app.scholarship.title}")
print(f"  Current Status: {under_review_app.status}")
print(f"  Reviewed by: {under_review_app.reviewed_by.get_full_name() if under_review_app.reviewed_by else 'None'}")

# Get OSAS user
osas_user = User.objects.filter(profile__user_type='osas').first()

if not osas_user:
    print("\nNo OSAS user found!")
    exit()

print(f"\nOSAS User: {osas_user.get_full_name()}")

# Simulate OSAS recommendation for approval
print("\n" + "-" * 60)
print("Simulating OSAS recommendation for APPROVAL...")
print("-" * 60)

under_review_app.mark_as_reviewed(
    reviewer=osas_user,
    status='osas_approved',
    comments='Test recommendation: Student meets all requirements and demonstrates excellent academic performance.'
)

print(f"✓ Application status changed to: {under_review_app.status}")
print(f"✓ Reviewed by: {under_review_app.reviewed_by.get_full_name()}")
print(f"✓ Reviewed at: {under_review_app.reviewed_at}")

# Create notifications for admins
admins = User.objects.filter(profile__user_type='admin')
print(f"\n✓ Creating notifications for {admins.count()} admin(s)...")

for admin in admins:
    Notification.objects.create(
        recipient=admin,
        title='New Application Recommended for Approval',
        message=f'OSAS staff {osas_user.get_full_name()} recommends approval for {under_review_app.student.get_full_name()}\'s application to {under_review_app.scholarship.title}.',
        notification_type='info',
        related_application=under_review_app
    )
    print(f"  - Notification sent to {admin.get_full_name()}")

# Verify it appears in pending approvals
print("\n" + "-" * 60)
print("Verifying pending approvals...")
print("-" * 60)

pending_approvals = Application.objects.filter(
    status__in=['osas_approved', 'osas_rejected']
)

print(f"\nTotal applications awaiting admin decision: {pending_approvals.count()}")
for app in pending_approvals:
    print(f"  - {app.student.get_full_name()} -> {app.scholarship.title}")
    print(f"    Status: {app.get_status_display()}")
    print(f"    Recommended by: {app.reviewed_by.get_full_name()}")
    print()

print("=" * 60)
print("SUCCESS!")
print("=" * 60)
print("\nNow log in as an admin user and navigate to:")
print("  Dashboard > Pending Final Approvals")
print("\nYou should see the application waiting for final decision.")
print("=" * 60)
