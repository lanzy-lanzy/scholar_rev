"""
Quick check for OSAS user configuration.
Run with: python manage.py shell < check_osas_user.py
"""

from django.contrib.auth.models import User

print("=" * 60)
print("CHECKING OSAS USER CONFIGURATION")
print("=" * 60)

try:
    user = User.objects.get(username='osas_staff')
    print(f"\n✓ User found: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  First name: {user.first_name}")
    print(f"  Last name: {user.last_name}")
    print(f"\nProfile Information:")
    print(f"  User type: {user.profile.user_type}")
    print(f"  Is OSAS: {user.profile.is_osas}")
    print(f"  Is Admin: {user.profile.is_admin}")
    print(f"  Is Student: {user.profile.is_student}")
    
    if user.profile.is_osas:
        print("\n✓ OSAS configuration is CORRECT!")
        print("  User should be able to access review pages.")
    else:
        print("\n✗ OSAS configuration is WRONG!")
        print(f"  Current type: {user.profile.user_type}")
        print("\nTo fix, run these commands:")
        print("  >>> from django.contrib.auth.models import User")
        print("  >>> user = User.objects.get(username='osas_staff')")
        print("  >>> user.profile.user_type = 'osas'")
        print("  >>> user.profile.save()")
        print("  >>> print('Fixed!')")
        
except User.DoesNotExist:
    print("\n✗ OSAS user does NOT exist!")
    print("  Run: python manage.py create_osas_user")

print("\n" + "=" * 60)
