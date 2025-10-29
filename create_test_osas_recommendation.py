"""
Create a fresh OSAS recommendation for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from core.models import Application, User, Notification

# Get a pending application
pending_apps = Application.objects.filter(status='pending')

if pending_apps.count() == 0:
    print("No pending applications available for testing.")
    exit()

app = pending_apps.first()
osas_user = User.objects.filter(profile__user_type='osas').first()

print(f"Creating OSAS recommendation for:")
print(f"  Student: {app.student.get_full_name()}")
print(f"  Scholarship: {app.scholarship.title}")
print(f"  OSAS Reviewer: {osas_user.get_full_name()}")

# Mark as reviewed with OSAS approval
app.mark_as_reviewed(
    reviewer=osas_user,
    status='osas_approved',
    comments='Test: Student demonstrates strong academic performance and meets all eligibility criteria. Recommend for approval.'
)

print(f"\n✓ Status changed to: {app.status}")

# Create notifications for admins
admins = User.objects.filter(profile__user_type='admin')
for admin in admins:
    Notification.objects.create(
        recipient=admin,
        title='New Application Recommended for Approval',
        message=f'OSAS staff {osas_user.get_full_name()} recommends approval for {app.student.get_full_name()}\'s application to {app.scholarship.title}.',
        notification_type='info',
        related_application=app
    )

print(f"✓ Notifications sent to {admins.count()} admin(s)")
print("\n✅ Done! Admin can now see this in Pending Final Approvals")
