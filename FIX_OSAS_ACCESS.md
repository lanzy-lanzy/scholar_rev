# 🔧 URGENT FIX: Access Denied Error

## 🎯 Error Message
```
Access denied. Administrator access required.
```

## ✅ Quick Fix

The OSAS user profile might not be set correctly. Run these commands:

### Step 1: Check Current Configuration
```powershell
python manage.py shell < check_osas_user.py
```

### Step 2: Fix OSAS User Profile
```powershell
python manage.py shell
```

Then run:
```python
from django.contrib.auth.models import User

# Get OSAS user
user = User.objects.get(username='osas_staff')

# Fix the profile
user.profile.user_type = 'osas'
user.profile.save()

# Verify
print(f"User type: {user.profile.user_type}")
print(f"Is OSAS: {user.profile.is_osas}")
print("✓ Fixed!")

# Exit
exit()
```

### Step 3: Logout and Login Again
1. Logout from the application
2. Login again with:
   - Username: `osas_staff`
   - Password: `osas123`
3. Try accessing Review Queue again

---

## 🔍 Why This Happens

The error "Administrator access required" means the view is checking for admin access, but you're logged in as OSAS. This happens when:

1. The OSAS user's `user_type` field is not set to `'osas'`
2. The `is_osas` property returns `False`
3. The view denies access

---

## 🚀 Alternative: One-Line Fix

Run this single command:
```powershell
python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='osas_staff'); u.profile.user_type = 'osas'; u.profile.save(); print('Fixed! User type:', u.profile.user_type, '| Is OSAS:', u.profile.is_osas)"
```

---

## ✅ Verification

After fixing, verify with:
```powershell
python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='osas_staff'); print('Is OSAS:', u.profile.is_osas)"
```

Should output: `Is OSAS: True`

---

## 🎯 Then Test

1. **Logout** from current session
2. **Login** as `osas_staff` / `osas123`
3. **Go to** Review Queue
4. **Click** "Review" button
5. **Should work!** ✓

---

## 📝 What the Fix Does

```python
user.profile.user_type = 'osas'  # Sets the user type to OSAS
user.profile.save()               # Saves to database

# This makes user.profile.is_osas return True
# Which allows access to OSAS views
```

---

## 🆘 If Still Not Working

Check which URL you're accessing:
- ✅ **Correct:** `http://127.0.0.1:8000/review/1/`
- ❌ **Wrong:** `http://127.0.0.1:8000/dashboard/admin/applications/1/review/`

The second URL is for admins only!

---

**Run the fix now and try again!** 🚀
