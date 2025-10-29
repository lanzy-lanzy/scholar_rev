"""
Test that OSAS review recommendations are working correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import Application

print("=" * 70)
print("TESTING OSAS REVIEW FIX")
print("=" * 70)

# Get OSAS user
osas_user = User.objects.filter(profile__user_type='osas').first()
if not osas_user:
    print("\n❌ No OSAS user found!")
    exit()

print(f"\n✓ OSAS User: {osas_user.username}")

# Get a pending application
pending_app = Application.objects.filter(status='pending').first()
if not pending_app:
    print("\n❌ No pending applications found!")
    exit()

print(f"✓ Test Application: {pending_app.student.get_full_name()} -> {pending_app.scholarship.title}")
print(f"  Current Status: {pending_app.status}")

# Create a test client and log in as OSAS
client = Client()
login_success = client.login(username=osas_user.username, password='osas123')  # Adjust password as needed

if not login_success:
    print("\n⚠️  Could not log in with test credentials")
    print("   This test requires manual verification through the web interface")
    print("\nMANUAL TEST STEPS:")
    print("1. Log in as OSAS user")
    print("2. Go to Review Queue")
    print(f"3. Click on application: {pending_app.student.get_full_name()} -> {pending_app.scholarship.title}")
    print("4. Select 'Recommend for Approval'")
    print("5. Add comments")
    print("6. Click 'Submit Review'")
    print("7. Check if status changes to 'osas_approved'")
else:
    print("\n✓ Logged in successfully")
    
    # Try to submit a review
    print("\nAttempting to submit OSAS recommendation...")
    response = client.post(
        f'/review/{pending_app.id}/',
        {
            'action': 'approve',
            'comments': 'Test recommendation - automated test'
        }
    )
    
    print(f"Response status: {response.status_code}")
    
    # Refresh the application from database
    pending_app.refresh_from_db()
    
    print(f"\nApplication status after POST: {pending_app.status}")
    
    if pending_app.status == 'osas_approved':
        print("\n✅ SUCCESS! OSAS recommendation is working correctly!")
        print(f"   Status changed to: {pending_app.get_status_display()}")
        print(f"   Reviewed by: {pending_app.reviewed_by.get_full_name()}")
        print(f"   Comments: {pending_app.reviewer_comments}")
    else:
        print(f"\n❌ FAILED! Status is still: {pending_app.status}")
        print("   Expected: osas_approved")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
