"""
Test the scholarship awardees page to ensure it renders without errors
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from core.views import scholarship_awardees

print("=" * 70)
print("TESTING SCHOLARSHIP AWARDEES PAGE")
print("=" * 70)

# Create a test client
client = Client()

# Get or create an admin user
try:
    admin_user = User.objects.filter(profile__user_type='admin').first()
    if not admin_user:
        print("❌ No admin user found. Please create an admin user first.")
        exit(1)
    
    print(f"\n✓ Using admin user: {admin_user.username}")
    
    # Log in as admin
    client.force_login(admin_user)
    print("✓ Logged in as admin")
    
    # Try to access the page
    print("\n" + "-" * 70)
    print("Attempting to access /scholarship-awardees/...")
    print("-" * 70)
    
    response = client.get('/scholarship-awardees/', HTTP_HOST='127.0.0.1')
    
    print(f"\nResponse Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Page loaded without errors")
        print(f"Content length: {len(response.content)} bytes")
        
        # Check if the page contains expected content
        content = response.content.decode('utf-8')
        
        checks = [
            ('Title present', 'Scholarship Awardees' in content),
            ('Statistics section', 'Total Awardees' in content),
            ('Export buttons', 'Export CSV' in content or 'Export PDF' in content),
            ('View toggle', 'Cards' in content or 'Table' in content),
        ]
        
        print("\nContent Checks:")
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
        
        # Check for template errors in content
        if '{{' in content or '}}' in content or '{%' in content or '%}' in content:
            print("\n⚠️  WARNING: Found unrendered template tags in output!")
            print("This means Django is not evaluating the templates properly.")
            # Find and show the first few occurrences
            import re
            tags = re.findall(r'\{\{[^}]+\}\}|\{%[^%]+%\}', content)
            if tags:
                print("\nFirst few unrendered tags:")
                for tag in tags[:5]:
                    print(f"  - {tag}")
        else:
            print("\n✅ No unrendered template tags found")
            
    elif response.status_code == 500:
        print("❌ FAILED! Server error (500)")
        print("\nThis usually means there's a template syntax error.")
        print("Check the error details above.")
    else:
        print(f"❌ FAILED! Unexpected status code: {response.status_code}")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 70)
