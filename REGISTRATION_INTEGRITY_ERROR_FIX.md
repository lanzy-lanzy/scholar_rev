# Registration IntegrityError Fix

## Error
```
IntegrityError at /auth/register/
UNIQUE constraint failed: core_userprofile.user_id
```

## Root Cause

The application has a **signal** (`core/signals.py`) that automatically creates a `UserProfile` when a `User` is created:

```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, user_type='student')
```

The registration form was **also** trying to create a `UserProfile`, causing a duplicate:

```python
# OLD CODE (WRONG)
profile = UserProfile.objects.create(user=user, ...)  # ❌ Tries to create again
```

## Solution

Changed the form to **update** the existing profile instead of creating a new one:

```python
# NEW CODE (CORRECT)
profile = user.profile  # Get the profile created by signal
profile.user_type = self.cleaned_data['user_type']
profile.student_id = self.cleaned_data.get('student_id')
profile.campus = self.cleaned_data.get('campus')
# ... update other fields
profile.save()  # ✅ Update existing profile
```

## What Changed

### File: `core/forms.py`

**Before:**
```python
def save(self, commit=True):
    user = super().save(commit=False)
    # ... set user fields
    
    if commit:
        user.save()
        # ❌ Creates new profile (causes error)
        profile = UserProfile.objects.create(
            user=user,
            user_type=self.cleaned_data['user_type'],
            # ...
        )
    return user
```

**After:**
```python
def save(self, commit=True):
    user = super().save(commit=False)
    # ... set user fields
    
    if commit:
        user.save()
        # ✅ Updates existing profile (no error)
        profile = user.profile
        profile.user_type = self.cleaned_data['user_type']
        profile.student_id = self.cleaned_data.get('student_id')
        profile.campus = self.cleaned_data.get('campus')
        profile.year_level = self.cleaned_data.get('year_level')
        profile.department = self.cleaned_data.get('department')
        profile.phone_number = self.cleaned_data.get('phone_number')
        profile.save()
    return user
```

## How It Works Now

### Registration Flow:

1. **User fills registration form**
2. **Form submits**
3. **User object created** (`user.save()`)
4. **Signal fires automatically** → Creates UserProfile with default values
5. **Form updates profile** → Sets user_type, campus, etc.
6. **Profile saved** → All data stored correctly
7. **User logged in** → Redirected to dashboard

### Timeline:
```
Form Submit
    ↓
User.save()
    ↓
Signal: Create UserProfile (user_type='student')
    ↓
Form: Update UserProfile (user_type, campus, etc.)
    ↓
Profile.save()
    ↓
✅ Success!
```

## Testing

### Test Registration:
1. Go to: `http://127.0.0.1:8000/register/`
2. Fill out form:
   - Username: `newstudent`
   - Email: `new@example.com`
   - Account Type: `Student`
   - Campus: `Dumingag Campus`
   - Other required fields
3. Click "Create Account"
4. ✅ Should work without error
5. ✅ Redirected to Student Dashboard
6. ✅ Profile has correct campus and user type

### Verify Profile Created Correctly:
```python
# In Django shell
python manage.py shell

from django.contrib.auth.models import User
user = User.objects.get(username='newstudent')
print(user.profile.user_type)  # Should show 'student'
print(user.profile.campus)     # Should show 'dumingag'
```

## Why This Happened

### Signal Pattern (Good)
- Ensures every User has a UserProfile
- Automatic, no manual creation needed
- Prevents missing profiles

### Form Pattern (Was Wrong)
- Tried to create profile manually
- Conflicted with signal
- Caused duplicate creation attempt

### Solution (Now Correct)
- Signal creates profile
- Form updates profile
- No conflicts!

## Benefits of This Fix

✅ **No More Errors** - Registration works smoothly  
✅ **Data Integrity** - One profile per user  
✅ **Automatic Creation** - Signal handles it  
✅ **Flexible Updates** - Form can update any field  
✅ **Clean Code** - Separation of concerns  

## Alternative Approaches (Not Used)

### Option 1: Remove Signal
```python
# Could remove the signal and let form create profile
# ❌ Not recommended - signal is useful for other user creation methods
```

### Option 2: Check if Profile Exists
```python
# Could check and create only if doesn't exist
profile, created = UserProfile.objects.get_or_create(user=user)
# ✅ Would work but updating existing is cleaner
```

### Option 3: Disable Signal During Registration
```python
# Could temporarily disable signal
# ❌ Complex and error-prone
```

## Related Files

- `core/forms.py` - Fixed form save method
- `core/signals.py` - Signal that creates profile (unchanged)
- `core/models.py` - UserProfile model (unchanged)
- `core/views.py` - Registration view (unchanged)

## Future Considerations

### If Adding More User Creation Methods:
- Admin panel user creation
- API user registration
- Social auth integration
- Bulk user import

All will benefit from the signal automatically creating profiles!

## Rollback Plan

If issues arise, revert to creating profile in form:

```python
# Revert code (not recommended)
try:
    profile = user.profile
except UserProfile.DoesNotExist:
    profile = UserProfile.objects.create(user=user)

# Then update fields...
```

---

**Status:** ✅ FIXED  
**Impact:** Registration now works without errors  
**Testing:** Ready for testing  
**Action:** Try registering a new user!
