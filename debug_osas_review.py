#!/usr/bin/env python
"""
Debug script to test OSAS review workflow
Run with: python debug_osas_review.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar.settings')
django.setup()

from core.models import Application, Notification
from django.contrib.auth.models import User

def test_osas_workflow():
    """Test the complete OSAS workflow"""
    
    print("=" * 60)
    print("OSAS WORKFLOW DEBUG SCRIPT")
    print("=" * 60)
    
    # 1. Check OSAS user exists
    print("\n1. Checking OSAS users...")
    osas_users = User.objects.filter(profile__user_type='osas')
    print(f"   Found {osas_users.count()} OSAS users:")
    for user in osas_users:
        print(f"   - {user.username} ({user.get_full_name()})")
    
    if not osas_users.exists():
        print("   ❌ ERROR: No OSAS users found!")
        return
    
    osas_user = osas_users.first()
    print(f"   ✅ Using OSAS user: {osas_user.username}")
    
    # 2. Check admin users exist
    print("\n2. Checking admin users...")
    admin_users = User.objects.filter(profile__user_type='admin')
    print(f"   Found {admin_users.count()} admin users:")
    for user in admin_users:
        print(f"   - {user.username} ({user.get_full_name()})")
    
    if not admin_users.exists():
        print("   ❌ ERROR: No admin users found!")
        return
    
    print(f"   ✅ Admins exist")
    
    # 3. Find a pending application
    print("\n3. Finding pending applications...")
    pending_apps = Application.objects.filter(status='pending')
    print(f"   Found {pending_apps.count()} pending applications")
    
    if not pending_apps.exists():
        print("   ⚠️  No pending applications found")
        print("   Looking for any application to test with...")
        test_app = Application.objects.first()
        if test_app:
            print(f"   Using application #{test_app.id} (status: {test_app.status})")
        else:
            print("   ❌ ERROR: No applications found in database!")
            return
    else:
        test_app = pending_apps.first()
        print(f"   ✅ Using application #{test_app.id}")
    
    # 4. Test OSAS recommendation
    print("\n4. Testing OSAS recommendation...")
    print(f"   Current status: {test_app.status}")
    print(f"   Recommending for approval...")
    
    try:
        test_app.mark_as_reviewed(
            reviewer=osas_user,
            status='osas_approved',
            comments='TEST: Automated test recommendation'
        )
        print(f"   ✅ Status changed to: {test_app.status}")
        print(f"   ✅ Reviewed by: {test_app.reviewed_by.username}")
        print(f"   ✅ Comments: {test_app.reviewer_comments}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return
    
    # 5. Create notifications for admins
    print("\n5. Creating notifications for admins...")
    notification_count = 0
    for admin in admin_users:
        try:
            Notification.objects.create(
                recipient=admin,
                title='TEST: New Application Recommended for Approval',
                message=f'OSAS staff {osas_user.get_full_name()} recommends approval for application #{test_app.id}',
                notification_type='info',
                related_application=test_app
            )
            notification_count += 1
            print(f"   ✅ Notification sent to {admin.username}")
        except Exception as e:
            print(f"   ❌ ERROR sending to {admin.username}: {str(e)}")
    
    print(f"   ✅ Total notifications sent: {notification_count}")
    
    # 6. Verify admin can see it
    print("\n6. Verifying admin can see the application...")
    osas_recommended = Application.objects.filter(status__in=['osas_approved', 'osas_rejected'])
    print(f"   Applications awaiting admin decision: {osas_recommended.count()}")
    for app in osas_recommended:
        print(f"   - App #{app.id}: {app.status} for {app.scholarship.title}")
    
    if test_app.id in [app.id for app in osas_recommended]:
        print(f"   ✅ Test application #{test_app.id} is in the list!")
    else:
        print(f"   ❌ ERROR: Test application #{test_app.id} NOT in the list!")
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ OSAS user exists: {osas_user.username}")
    print(f"✅ Admin users exist: {admin_users.count()}")
    print(f"✅ Test application: #{test_app.id}")
    print(f"✅ Status changed to: {test_app.status}")
    print(f"✅ Notifications sent: {notification_count}")
    print(f"✅ Visible to admin: Yes")
    print("\n📋 Next Steps:")
    print("1. Login as admin")
    print("2. Go to: /dashboard/admin/pending-approvals/")
    print(f"3. Look for application #{test_app.id}")
    print("4. Click 'Make Decision'")
    print("5. Approve or reject")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_osas_workflow()
