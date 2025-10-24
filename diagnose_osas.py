"""
Diagnostic script for OSAS review functionality.
Run with: python manage.py shell < diagnose_osas.py
"""

from django.contrib.auth.models import User
from core.models import Application, UserProfile

print("=" * 70)
print("OSAS REVIEW FUNCTIONALITY DIAGNOSTIC")
print("=" * 70)

# 1. Check OSAS User
print("\n1. CHECKING OSAS USER...")
print("-" * 70)
try:
    osas_user = User.objects.get(username='osas_staff')
    print(f"✓ OSAS user exists: {osas_user.username}")
    print(f"  Email: {osas_user.email}")
    print(f"  User type: {osas_user.profile.user_type}")
    print(f"  Is OSAS: {osas_user.profile.is_osas}")
    print(f"  Is authenticated: True (when logged in)")
    
    if not osas_user.profile.is_osas:
        print("\n  ⚠️  WARNING: User profile is NOT set to OSAS!")
        print("  Run this to fix:")
        print("  >>> user = User.objects.get(username='osas_staff')")
        print("  >>> user.profile.user_type = 'osas'")
        print("  >>> user.profile.save()")
    else:
        print("  ✓ User profile correctly set to OSAS")
except User.DoesNotExist:
    print("✗ OSAS user does NOT exist!")
    print("  Run: python manage.py create_osas_user")

# 2. Check Applications
print("\n2. CHECKING APPLICATIONS...")
print("-" * 70)
apps = Application.objects.all()
print(f"Total applications: {apps.count()}")

if apps.count() == 0:
    print("✗ No applications found!")
    print("  Run: python manage.py create_test_applications")
else:
    print("\nApplications by status:")
    for status in ['pending', 'under_review', 'approved', 'rejected']:
        count = apps.filter(status=status).count()
        print(f"  {status}: {count}")
    
    print("\nSample applications:")
    for app in apps[:5]:
        print(f"  ID: {app.id} | Student: {app.student.username} | " +
              f"Scholarship: {app.scholarship.title[:30]}... | Status: {app.status}")

# 3. Check URLs
print("\n3. CHECKING URL CONFIGURATION...")
print("-" * 70)
from django.urls import reverse
try:
    # Test URL patterns
    test_app_id = apps.first().id if apps.exists() else 1
    
    urls_to_test = [
        ('core:osas_dashboard', {}, 'OSAS Dashboard'),
        ('core:review_queue', {}, 'Review Queue'),
        ('core:review_application', {'application_id': test_app_id}, 'Review Application'),
        ('core:assign_application', {'application_id': test_app_id}, 'Assign Application'),
        ('core:submit_review', {'application_id': test_app_id}, 'Submit Review'),
    ]
    
    for url_name, kwargs, description in urls_to_test:
        try:
            url = reverse(url_name, kwargs=kwargs)
            print(f"✓ {description}: {url}")
        except Exception as e:
            print(f"✗ {description}: ERROR - {e}")
            
except Exception as e:
    print(f"✗ Error checking URLs: {e}")

# 4. Check Templates
print("\n4. CHECKING TEMPLATES...")
print("-" * 70)
import os
from django.conf import settings

templates_to_check = [
    'osas/dashboard.html',
    'osas/review_queue.html',
    'osas/application_review.html',
]

for template_path in templates_to_check:
    found = False
    for template_dir in settings.TEMPLATES[0]['DIRS']:
        full_path = os.path.join(template_dir, template_path)
        if os.path.exists(full_path):
            print(f"✓ {template_path}: Found")
            found = True
            break
    if not found:
        print(f"✗ {template_path}: NOT FOUND")

# 5. Summary
print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)

issues = []

try:
    osas_user = User.objects.get(username='osas_staff')
    if not osas_user.profile.is_osas:
        issues.append("OSAS user profile not set to 'osas' type")
except:
    issues.append("OSAS user does not exist")

if apps.count() == 0:
    issues.append("No applications in database")

if len(issues) == 0:
    print("✓ ALL CHECKS PASSED!")
    print("\nYou should be able to:")
    print("  1. Login as osas_staff")
    print("  2. Access Review Queue")
    print("  3. Click 'Review' button")
    print("  4. See application details")
    print("  5. Submit review decisions")
else:
    print("⚠️  ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    print("\nFIXES:")
    if "OSAS user does not exist" in issues:
        print("  → Run: python manage.py create_osas_user")
    if "OSAS user profile not set to 'osas' type" in issues:
        print("  → Run in shell:")
        print("    user = User.objects.get(username='osas_staff')")
        print("    user.profile.user_type = 'osas'")
        print("    user.profile.save()")
    if "No applications in database" in issues:
        print("  → Run: python manage.py create_test_applications")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
