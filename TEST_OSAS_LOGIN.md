# Testing OSAS Staff Login

## Issue
OSAS staff cannot redirect to their dashboard after login.

## Verification Steps

### 1. Check if OSAS User Exists
Run this in Django shell:
```python
python manage.py shell

from django.contrib.auth.models import User
from core.models import UserProfile

# Check all users and their types
for user in User.objects.all():
    profile = getattr(user, 'profile', None)
    if profile:
        print(f"Username: {user.username}, Type: {profile.user_type}, is_osas: {profile.is_osas}")
```

### 2. Create OSAS User (if needed)
```python
python manage.py shell

from django.contrib.auth.models import User
from core.models import UserProfile

# Create OSAS user
user = User.objects.create_user(
    username='osas_staff',
    email='osas@example.com',
    password='osas123',
    first_name='OSAS',
    last_name='Staff'
)

# Set user type to OSAS
user.profile.user_type = 'osas'
user.profile.save()

print(f"Created OSAS user: {user.username}")
print(f"User type: {user.profile.user_type}")
print(f"Is OSAS: {user.profile.is_osas}")
```

### 3. Test Login Flow
1. Go to `/auth/login/`
2. Login with OSAS credentials
3. Should redirect to `/dashboard/` (dashboard_router)
4. Dashboard router should detect `user_type == 'osas'`
5. Should redirect to `/osas/` (osas_dashboard)

### 4. Check Current Configuration

**Settings (scholar_/settings.py):**
```python
LOGIN_REDIRECT_URL = 'core:dashboard_router'  ✓ Correct
```

**URLs (core/urls.py):**
```python
path('dashboard/', views.dashboard_router, name='dashboard_router'),  ✓
path('osas/', views.osas_dashboard, name='osas_dashboard'),  ✓
```

**Dashboard Router (core/views.py):**
```python
def dashboard_router(request):
    if user_profile.user_type == 'osas':
        return redirect('core:osas_dashboard')  ✓ Correct
```

**OSAS Dashboard (core/views.py):**
```python
def osas_dashboard(request):
    if not request.user.profile.is_osas:
        messages.error(request, 'Access denied.')
        return redirect('core:landing_page')
    # ... rest of code
    return render(request, 'osas/dashboard.html', context)  ✓ Correct
```

**Template exists:**
```
templates/osas/dashboard.html  ✓ Exists
```

## Possible Issues

### Issue 1: OSAS User Doesn't Exist
**Solution:** Create OSAS user using the script above

### Issue 2: User Type Not Set to 'osas'
**Solution:** Update user profile:
```python
user = User.objects.get(username='your_osas_username')
user.profile.user_type = 'osas'
user.profile.save()
```

### Issue 3: Profile Not Created
**Solution:** Ensure signal creates profile:
```python
# Check if signal exists in core/models.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
```

## Quick Fix Script

Create and run this management command:

**File: core/management/commands/create_osas_user.py**
```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile

class Command(BaseCommand):
    help = 'Create OSAS staff user'

    def handle(self, *args, **kwargs):
        username = 'osas_staff'
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(f'User {username} already exists')
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email='osas@example.com',
                password='osas123',
                first_name='OSAS',
                last_name='Staff'
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        
        # Ensure profile exists and set type
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.user_type = 'osas'
        profile.save()
        
        self.stdout.write(self.style.SUCCESS(f'User type set to: {profile.user_type}'))
        self.stdout.write(self.style.SUCCESS(f'Is OSAS: {profile.is_osas}'))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Password: osas123')
```

Run with:
```bash
python manage.py create_osas_user
```

## Testing After Fix

1. **Login:** Go to `/auth/login/`
2. **Credentials:** 
   - Username: `osas_staff`
   - Password: `osas123`
3. **Expected:** Should redirect to OSAS dashboard at `/osas/`
4. **Verify:** Should see OSAS dashboard with review queue

## Debug Mode

If still not working, add debug prints to `dashboard_router`:

```python
def dashboard_router(request):
    if not request.user.is_authenticated:
        return redirect('core:landing_page')
    
    user_profile = getattr(request.user, 'profile', None)
    
    # DEBUG
    print(f"DEBUG: User: {request.user.username}")
    print(f"DEBUG: Profile exists: {user_profile is not None}")
    if user_profile:
        print(f"DEBUG: User type: {user_profile.user_type}")
        print(f"DEBUG: Is OSAS: {user_profile.is_osas}")
    
    if not user_profile:
        messages.error(request, 'User profile not found.')
        return redirect('core:landing_page')
    
    if user_profile.user_type == 'osas':
        print("DEBUG: Redirecting to OSAS dashboard")
        return redirect('core:osas_dashboard')
    # ... rest of code
```

Check console output when logging in.
