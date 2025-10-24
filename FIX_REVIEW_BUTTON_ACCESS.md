# 🔧 Fix: Can't Access Review Button

## 🎯 Problem
When clicking the "Review" button in the Review Queue, you can't access the review page.

## ✅ Verified Components

I've checked all the components and they are correct:
- ✅ URL pattern exists: `path('review/<int:application_id>/', views.review_application, name='review_application')`
- ✅ View function exists and has proper access control
- ✅ Template exists: `templates/osas/application_review.html`
- ✅ Template has review form with decision options

## 🔍 Possible Issues & Solutions

### Issue 1: Access Denied Error
**Symptom:** Redirected to landing page with "Access denied" message

**Cause:** OSAS user profile not set correctly

**Solution:**
```powershell
python manage.py shell
```
```python
from django.contrib.auth.models import User

# Check OSAS user
user = User.objects.get(username='osas_staff')
print(f"User type: {user.profile.user_type}")
print(f"Is OSAS: {user.profile.is_osas}")

# If not OSAS, fix it:
if not user.profile.is_osas:
    user.profile.user_type = 'osas'
    user.profile.save()
    print("✓ Fixed! User is now OSAS")
```

---

### Issue 2: 404 Not Found Error
**Symptom:** Page not found error

**Cause:** URL pattern mismatch

**Solution:** Check the URL in browser. Should be:
```
http://127.0.0.1:8000/review/1/
```

If it's different, the template link might be wrong.

---

### Issue 3: Template Error
**Symptom:** Template rendering error

**Cause:** Missing template or syntax error

**Solution:** Check server console for error details

---

### Issue 4: Application ID Invalid
**Symptom:** Application does not exist error

**Cause:** Trying to review non-existent application

**Solution:** Verify application exists:
```python
python manage.py shell

from core.models import Application
apps = Application.objects.all()
for app in apps:
    print(f"ID: {app.id}, Student: {app.student.username}, Status: {app.status}")
```

---

## 🚀 Quick Debug Steps

### Step 1: Check Browser Console
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Click "Review" button
4. Look for any JavaScript errors

### Step 2: Check Django Server Console
1. Look at the terminal where `python manage.py runserver` is running
2. Click "Review" button
3. Check for any error messages or stack traces

### Step 3: Verify URL
1. Click "Review" button
2. Check the URL in browser address bar
3. Should be: `http://127.0.0.1:8000/review/<number>/`

### Step 4: Test Direct Access
Try accessing directly:
```
http://127.0.0.1:8000/review/1/
```
Replace `1` with an actual application ID from your database.

---

## 🧪 Test the Full Workflow

### Complete Test:

1. **Login as OSAS:**
   ```
   Username: osas_staff
   Password: osas123
   ```

2. **Go to Review Queue:**
   ```
   http://127.0.0.1:8000/review-queue/
   ```

3. **Filter Pending:**
   - Set Status filter to "Pending"
   - Click "Apply Filters"

4. **Assign Application:**
   - Click "Assign to Me" on any application
   - Should see success message
   - Status changes to "Under Review"

5. **Click Review:**
   - Click "Review" button
   - Should load review page with application details

6. **Make Decision:**
   - Select decision (Approve/Reject/Request Info)
   - Add comments
   - Click "Submit Review"
   - Should redirect to Review Queue

---

## 🔧 Manual Fix: Update View (If Needed)

If the issue persists, let's add better error handling:

### Check Current View:
The view at line 693 in `core/views.py` should look like this:

```python
@login_required
def review_application(request, application_id):
    """OSAS view to review individual application."""
    if not request.user.profile.is_osas:
        messages.error(request, 'Access denied. OSAS staff access required.')
        return redirect('core:landing_page')
    
    application = get_object_or_404(
        Application.objects.select_related('student', 'scholarship', 'reviewed_by'),
        id=application_id
    )
    
    context = {
        'application': application,
    }
    
    return render(request, 'osas/application_review.html', context)
```

### Add Debug Output (Temporary):
Add this at the start of the view to debug:

```python
@login_required
def review_application(request, application_id):
    """OSAS view to review individual application."""
    
    # DEBUG
    print(f"DEBUG: User: {request.user.username}")
    print(f"DEBUG: Is OSAS: {request.user.profile.is_osas}")
    print(f"DEBUG: Application ID: {application_id}")
    
    if not request.user.profile.is_osas:
        messages.error(request, 'Access denied. OSAS staff access required.')
        return redirect('core:landing_page')
    
    # ... rest of code
```

Then check the server console when clicking "Review".

---

## 📊 Verify Database

### Check Applications:
```powershell
python manage.py shell
```

```python
from core.models import Application

# List all applications
apps = Application.objects.all()
print(f"Total applications: {apps.count()}")

for app in apps:
    print(f"\nID: {app.id}")
    print(f"  Student: {app.student.get_full_name()}")
    print(f"  Scholarship: {app.scholarship.title}")
    print(f"  Status: {app.status}")
    print(f"  Reviewed by: {app.reviewed_by}")
```

### Check OSAS User:
```python
from django.contrib.auth.models import User

user = User.objects.get(username='osas_staff')
print(f"Username: {user.username}")
print(f"User type: {user.profile.user_type}")
print(f"Is OSAS: {user.profile.is_osas}")
print(f"Is authenticated: {user.is_authenticated}")
```

---

## 🎯 Expected Behavior

When clicking "Review" button:

1. **URL Changes to:** `/review/<application_id>/`
2. **Page Loads:** Application review page
3. **Shows:**
   - Student information
   - Scholarship details
   - Personal statement
   - GPA and additional info
   - Review decision form (if not already reviewed)
   - Quick actions sidebar

4. **Can:**
   - Assign to self (if pending)
   - Select decision (Approve/Reject/Request Info)
   - Add comments
   - Submit review
   - Contact student via email
   - Return to queue

---

## 🐛 Common Error Messages

### "Access denied. OSAS staff access required."
**Fix:** User profile not set to OSAS
```python
user = User.objects.get(username='osas_staff')
user.profile.user_type = 'osas'
user.profile.save()
```

### "Application matching query does not exist."
**Fix:** Invalid application ID
- Check application exists in database
- Verify ID in URL matches database

### "TemplateDoesNotExist at /review/1/"
**Fix:** Template file missing
- Verify file exists: `templates/osas/application_review.html`
- Check template path in view

---

## 📝 Quick Checklist

Before reporting the issue, verify:

- [ ] OSAS user logged in (`osas_staff`)
- [ ] User profile type is 'osas'
- [ ] Applications exist in database
- [ ] Review Queue shows applications
- [ ] Can see "Review" button
- [ ] Clicked "Review" button
- [ ] Check browser URL after click
- [ ] Check server console for errors
- [ ] Check browser console for errors

---

## 🆘 If Still Not Working

### Provide This Information:

1. **Browser URL after clicking Review:**
   ```
   Example: http://127.0.0.1:8000/review/1/
   ```

2. **Error message shown (if any):**
   ```
   Example: "Access denied" or "Page not found"
   ```

3. **Server console output:**
   ```
   Copy the error from terminal
   ```

4. **User verification:**
   ```powershell
   python manage.py shell
   
   from django.contrib.auth.models import User
   user = User.objects.get(username='osas_staff')
   print(f"Is OSAS: {user.profile.is_osas}")
   ```

---

## ✅ Expected Working Flow

```
1. Login as osas_staff ✓
2. Go to Review Queue ✓
3. See applications listed ✓
4. Click "Review" button ✓
5. URL: /review/1/ ✓
6. Page loads with application details ✓
7. Review form visible ✓
8. Can submit decision ✓
```

If any step fails, note which one and check the corresponding solution above!

---

## 🎉 Summary

The review functionality is fully implemented. If you're having access issues:

1. **Verify OSAS user profile** is set correctly
2. **Check server console** for error messages
3. **Test direct URL access** to `/review/1/`
4. **Ensure applications exist** in database

Most likely cause: User profile not set to 'osas' type. Run the fix command above! 🚀
