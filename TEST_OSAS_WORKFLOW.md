# Testing OSAS Workflow - Troubleshooting Guide

## Current Status
✅ Backend is working correctly
✅ Database can store `osas_approved` and `osas_rejected` statuses
✅ Admin user exists
✅ OSAS user exists
✅ Application with `osas_approved` status exists in database

## Issue
When OSAS staff clicks "Submit Review" in the browser, the form doesn't seem to submit or the status doesn't change.

## Possible Causes

### 1. JavaScript Interference
**Check**: Browser console for errors
**Solution**: Open browser DevTools (F12) → Console tab → Look for red errors

### 2. Form Not Submitting
**Check**: Network tab in DevTools
**Solution**: 
1. Open DevTools (F12)
2. Go to Network tab
3. Click "Submit Review"
4. Look for POST request to `/review/<id>/`
5. Check response status

### 3. CSRF Token Issue
**Check**: Form has CSRF token
**Solution**: View page source, search for `csrfmiddlewaretoken`

### 4. Permission Issue
**Check**: User is actually OSAS staff
**Solution**: Verify in Django admin or database

## Step-by-Step Testing

### Test 1: Verify User Type
```bash
python manage.py shell -c "from django.contrib.auth.models import User; user = User.objects.get(username='YOUR_USERNAME'); print('User type:', user.profile.user_type); print('Is OSAS:', user.profile.is_osas)"
```

Replace `YOUR_USERNAME` with the OSAS username you're logged in as.

### Test 2: Check Application Status
```bash
python manage.py shell -c "from core.models import Application; app = Application.objects.get(id=YOUR_APP_ID); print('Status:', app.status); print('Can review:', app.status not in ['approved', 'rejected'])"
```

Replace `YOUR_APP_ID` with the application ID you're trying to review.

### Test 3: Manual Status Change (Bypass Form)
```bash
python manage.py shell -c "from core.models import Application; from django.contrib.auth.models import User; osas = User.objects.get(username='YOUR_USERNAME'); app = Application.objects.get(id=YOUR_APP_ID); app.mark_as_reviewed(reviewer=osas, status='osas_approved', comments='Manual test'); print('Success! New status:', app.status)"
```

### Test 4: Check Admin Can See It
```bash
python manage.py shell -c "from core.models import Application; apps = Application.objects.filter(status__in=['osas_approved', 'osas_rejected']); print('Count:', apps.count()); print('IDs:', [a.id for a in apps])"
```

Then login as admin and go to: `/dashboard/admin/pending-approvals/`

## Browser Testing Checklist

### Before Submitting
- [ ] Logged in as OSAS staff
- [ ] On application review page (`/review/<id>/`)
- [ ] Can see "Review Decision" form
- [ ] Dropdown shows 3 options
- [ ] Can select "Recommend for Approval"
- [ ] Can type in comments field

### When Submitting
- [ ] Click "Submit Review" button
- [ ] Button shows loading state (if implemented)
- [ ] Page redirects or shows message
- [ ] Success message appears
- [ ] Redirected to review queue

### After Submitting
- [ ] Application status changed in database
- [ ] Admin receives notification
- [ ] Application appears in admin pending approvals

## Common Issues & Solutions

### Issue 1: Form Submits But Nothing Happens
**Cause**: View is not processing POST correctly
**Solution**: Check Django logs for errors
```bash
# In terminal where Django is running, look for errors
```

### Issue 2: "Access Denied" Message
**Cause**: User is not OSAS staff
**Solution**: 
1. Go to Django admin
2. Find user
3. Check profile → user_type = 'osas'

### Issue 3: Form Doesn't Submit
**Cause**: JavaScript error or missing CSRF token
**Solution**:
1. Check browser console for errors
2. View page source
3. Search for `<input type="hidden" name="csrfmiddlewaretoken"`
4. Should exist in form

### Issue 4: Status Doesn't Change
**Cause**: Validation error or exception in view
**Solution**: Check Django logs for traceback

## Manual Workaround

If the form still doesn't work, you can manually change the status:

### Option 1: Django Admin
1. Go to `/admin/`
2. Click "Applications"
3. Find the application
4. Change status to "osas_approved" or "osas_rejected"
5. Add reviewer and comments
6. Save

### Option 2: Django Shell
```python
python manage.py shell

from core.models import Application
from django.contrib.auth.models import User

# Get OSAS user
osas = User.objects.get(username='osas_staff')

# Get application
app = Application.objects.get(id=28)  # Replace with actual ID

# Recommend for approval
app.mark_as_reviewed(
    reviewer=osas,
    status='osas_approved',
    comments='Recommended for approval - strong candidate'
)

print(f"Success! Status is now: {app.status}")

# Create notification for admin
from core.models import Notification
admins = User.objects.filter(profile__user_type='admin')
for admin in admins:
    Notification.objects.create(
        recipient=admin,
        title='New Application Recommended for Approval',
        message=f'OSAS staff recommends approval for application #{app.id}',
        notification_type='info',
        related_application=app
    )
print(f"Notifications sent to {admins.count()} admins")
```

## Debugging Steps

### Step 1: Enable Django Debug Mode
In `settings.py`:
```python
DEBUG = True
```

### Step 2: Check Django Logs
Look at terminal where `python manage.py runserver` is running

### Step 3: Add Print Statements
In `core/views.py`, add to `application_review` function:
```python
if request.method == 'POST':
    print("POST received!")  # Add this
    action = request.POST.get('action')
    print(f"Action: {action}")  # Add this
    comments = request.POST.get('comments', '')
    print(f"Comments: {comments}")  # Add this
```

### Step 4: Test Again
1. Submit form
2. Check terminal for print statements
3. If you see them, backend is working
4. If not, form isn't submitting

## Expected Behavior

### When OSAS Recommends Approval:
1. Click "Recommend for Approval"
2. Add comments
3. Click "Submit Review"
4. See message: "Application recommended for approval. Awaiting admin final decision."
5. Redirect to review queue
6. Application status = `osas_approved`
7. Admin receives notification

### When Admin Views Pending Approvals:
1. Login as admin
2. Go to dashboard
3. Click "Pending Final Approvals" (teal button)
4. See list of applications with `osas_approved` or `osas_rejected` status
5. Click "Make Decision"
6. Review and approve/reject

## Contact for Help

If issue persists:
1. Check all items in this guide
2. Collect error messages from:
   - Browser console
   - Django logs
   - Network tab
3. Note exact steps to reproduce
4. Share screenshots of errors

---

**Last Updated**: [Current Date]
**Status**: Troubleshooting in progress
