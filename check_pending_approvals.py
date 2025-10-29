"""
Debug script to check pending approvals status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from core.models import Application, User
from django.db.models import Q

print("=" * 60)
print("CHECKING PENDING APPROVALS STATUS")
print("=" * 60)

# Check all application statuses
print("\n1. All Application Statuses:")
print("-" * 60)
all_apps = Application.objects.all()
print(f"Total applications: {all_apps.count()}")

status_counts = {}
for app in all_apps:
    status = app.status
    status_counts[status] = status_counts.get(status, 0) + 1

for status, count in status_counts.items():
    print(f"   {status}: {count}")

# Check OSAS recommended applications
print("\n2. OSAS Recommended Applications:")
print("-" * 60)
osas_recommended = Application.objects.filter(
    status__in=['osas_approved', 'osas_rejected']
).select_related('student', 'scholarship', 'reviewed_by')

print(f"Total OSAS recommended: {osas_recommended.count()}")
for app in osas_recommended:
    print(f"   - {app.student.get_full_name()} -> {app.scholarship.title}")
    print(f"     Status: {app.status}")
    print(f"     Reviewed by: {app.reviewed_by.get_full_name() if app.reviewed_by else 'None'}")
    print(f"     Reviewed at: {app.reviewed_at}")
    print()

# Check if there are any pending applications
print("\n3. Pending Applications (not yet reviewed by OSAS):")
print("-" * 60)
pending = Application.objects.filter(status='pending')
print(f"Total pending: {pending.count()}")
for app in pending:
    print(f"   - {app.student.get_full_name()} -> {app.scholarship.title}")

# Check under review
print("\n4. Under Review by OSAS:")
print("-" * 60)
under_review = Application.objects.filter(status='under_review')
print(f"Total under review: {under_review.count()}")
for app in under_review:
    print(f"   - {app.student.get_full_name()} -> {app.scholarship.title}")
    print(f"     Reviewed by: {app.reviewed_by.get_full_name() if app.reviewed_by else 'None'}")

# Check admins
print("\n5. Admin Users:")
print("-" * 60)
admins = User.objects.filter(profile__user_type='admin')
print(f"Total admins: {admins.count()}")
for admin in admins:
    print(f"   - {admin.get_full_name()} ({admin.username})")

# Check OSAS users
print("\n6. OSAS Users:")
print("-" * 60)
osas_users = User.objects.filter(profile__user_type='osas')
print(f"Total OSAS users: {osas_users.count()}")
for osas in osas_users:
    print(f"   - {osas.get_full_name()} ({osas.username})")

print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)

if osas_recommended.count() == 0:
    print("No applications have been recommended by OSAS yet.")
    print("\nTo test the system:")
    print("1. Log in as OSAS user")
    print("2. Go to Review Queue")
    print("3. Review an application and recommend approval/rejection")
    print("4. Then log in as Admin to see it in Pending Approvals")
else:
    print(f"Found {osas_recommended.count()} applications awaiting admin decision.")
    print("Admins should be able to see these in the Pending Approvals page.")

print("\n" + "=" * 60)
