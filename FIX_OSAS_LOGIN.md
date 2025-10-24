# 🔧 Fix OSAS Staff Login - Complete Guide

## ✅ What I Fixed

I've verified that **all the code is correct** for OSAS login routing:
- ✓ Dashboard router checks for `user_type == 'osas'`
- ✓ Redirects to `core:osas_dashboard`
- ✓ OSAS dashboard view exists
- ✓ Template exists at `templates/osas/dashboard.html`
- ✓ URL routing is correct

## 🎯 The Actual Issue

The problem is likely that **you don't have an OSAS user created yet**, or the existing user's `user_type` is not set to `'osas'`.

---

## 🚀 Quick Fix (Recommended)

I've created a management command to easily create an OSAS user.

### Step 1: Run the Command

```powershell
python manage.py create_osas_user
```

This will:
- Create a user with username: `osas_staff`
- Set password to: `osas123`
- Set user_type to: `osas`
- Display all the details

### Step 2: Test Login

1. Go to: `http://localhost:8000/auth/login/`
2. Login with:
   - **Username:** `osas_staff`
   - **Password:** `osas123`
3. Should automatically redirect to OSAS dashboard at `/osas/`

---

## 🔧 Alternative: Create OSAS User Manually

If you prefer to create the user manually:

### Option 1: Django Shell

```powershell
python manage.py shell
```

Then run:
```python
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

print(f"✓ Created OSAS user: {user.username}")
print(f"✓ User type: {user.profile.user_type}")
print(f"✓ Is OSAS: {user.profile.is_osas}")
```

### Option 2: Update Existing User

If you already have a user and want to make them OSAS:

```python
from django.contrib.auth.models import User

# Get the user
user = User.objects.get(username='your_username_here')

# Change to OSAS
user.profile.user_type = 'osas'
user.profile.save()

print(f"✓ Updated {user.username} to OSAS staff")
```

---

## 🔍 Verify Setup

### Check All Users and Their Types

```powershell
python manage.py shell
```

```python
from django.contrib.auth.models import User

for user in User.objects.all():
    profile = getattr(user, 'profile', None)
    if profile:
        print(f"Username: {user.username:20} | Type: {profile.user_type:10} | Is OSAS: {profile.is_osas}")
```

---

## 📋 Login Flow Explanation

Here's how the login routing works:

```
1. User logs in at /auth/login/
        ↓
2. Django's LoginView authenticates user
        ↓
3. Redirects to LOGIN_REDIRECT_URL = 'core:dashboard_router'
        ↓
4. dashboard_router() checks user_profile.user_type
        ↓
5. If user_type == 'osas':
        ↓
6. Redirects to 'core:osas_dashboard' (/osas/)
        ↓
7. osas_dashboard() view renders templates/osas/dashboard.html
        ↓
8. ✓ OSAS staff sees their dashboard!
```

---

## 🎯 User Types in the System

The system supports 3 user types:

| User Type | Value | Dashboard URL | Description |
|-----------|-------|---------------|-------------|
| **Student** | `'student'` | `/student/` | Students applying for scholarships |
| **Admin** | `'admin'` | `/dashboard/admin/` | Administrators managing scholarships |
| **OSAS** | `'osas'` | `/osas/` | OSAS staff reviewing applications |

---

## 🐛 Troubleshooting

### Issue 1: "Access denied" message after login
**Cause:** User's `user_type` is not set to `'osas'`  
**Solution:** Run `python manage.py create_osas_user` or update manually

### Issue 2: Redirects to landing page instead of dashboard
**Cause:** User profile doesn't exist  
**Solution:** Ensure UserProfile is created (should happen automatically via signal)

### Issue 3: "User profile not found" error
**Cause:** Profile creation signal not working  
**Solution:** Manually create profile:
```python
from core.models import UserProfile
user = User.objects.get(username='osas_staff')
UserProfile.objects.get_or_create(user=user, defaults={'user_type': 'osas'})
```

### Issue 4: Wrong dashboard appears
**Cause:** User type is set to wrong value  
**Solution:** Check and update:
```python
user = User.objects.get(username='osas_staff')
print(f"Current type: {user.profile.user_type}")
user.profile.user_type = 'osas'
user.profile.save()
```

---

## ✅ Testing Checklist

After creating the OSAS user, verify:

- [ ] User exists in database
- [ ] User profile exists
- [ ] `user_profile.user_type == 'osas'`
- [ ] `user_profile.is_osas == True`
- [ ] Can login successfully
- [ ] Redirects to `/osas/` after login
- [ ] OSAS dashboard displays correctly
- [ ] Can access review queue
- [ ] Can review applications

---

## 📝 Custom Username/Password

If you want different credentials:

```powershell
python manage.py create_osas_user --username myosas --password mypass123 --email myosas@example.com
```

---

## 🎉 Summary

**The routing code is already correct!** You just need to:

1. **Run:** `python manage.py create_osas_user`
2. **Login:** with `osas_staff` / `osas123`
3. **Done:** Should redirect to OSAS dashboard automatically!

If you still have issues after running the command, let me know and I'll help debug further! 🚀
