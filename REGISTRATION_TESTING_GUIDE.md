# Registration Form - Testing Guide

## How the Multi-Step Registration Works

### Visual Flow

```
┌─────────────────────────────────────┐
│  Progress Bar: ████░░░░░░ (33%)    │
│  Step 1 of 3                        │
├─────────────────────────────────────┤
│                                     │
│  📝 Basic Information               │
│  • First Name                       │
│  • Last Name                        │
│  • Username                         │
│  • Email                            │
│  • Account Type                     │
│                                     │
│              [Next Step →]          │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Progress Bar: ████████░░ (67%)    │
│  Step 2 of 3                        │
├─────────────────────────────────────┤
│                                     │
│  🎓 Student Information             │
│  • Student ID                       │
│  • Campus                           │
│  • Year Level                       │
│  • Department (optional)            │
│  • Phone (optional)                 │
│                                     │
│  [← Previous]    [Next Step →]     │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Progress Bar: ████████████ (100%) │
│  Step 3 of 3                        │
├─────────────────────────────────────┤
│                                     │
│  🔒 Set Your Password               │
│  • Password                         │
│  • Confirm Password                 │
│                                     │
│  [← Previous]  [Create Account]    │
└─────────────────────────────────────┘
```

## Testing Steps

### 1. Open Registration Page
```
http://127.0.0.1:8000/register/
```

### 2. Verify Step 1 is Visible
You should see:
- ✅ Progress bar showing "Step 1 of 3" (33% filled)
- ✅ "Basic Information" heading
- ✅ First Name, Last Name, Username, Email fields
- ✅ Account Type dropdown
- ✅ "Next Step" button (blue)
- ❌ NO password fields visible yet
- ❌ NO student-specific fields visible yet

### 3. Fill Step 1 and Click "Next Step"
Fill in:
- First Name: `Test`
- Last Name: `Student`
- Username: `teststudent123`
- Email: `test@example.com`
- Account Type: `Student`

Click the blue "Next Step" button

### 4. Verify Step 2 Appears
You should see:
- ✅ Progress bar showing "Step 2 of 3" (67% filled)
- ✅ "Student Information" heading
- ✅ Student ID, Campus, Year Level fields
- ✅ Department and Phone fields
- ✅ "Previous" button (gray, left side)
- ✅ "Next Step" button (blue, right side)
- ❌ Step 1 fields are hidden
- ❌ Password fields still not visible

### 5. Fill Step 2 and Click "Next Step"
Fill in:
- Student ID: `2024-001`
- Campus: Select `Dumingag Campus`
- Year Level: Select `1st Year`
- Department: `Computer Science` (optional)
- Phone: `09123456789` (optional)

Click the blue "Next Step" button

### 6. Verify Step 3 Appears
You should see:
- ✅ Progress bar showing "Step 3 of 3" (100% filled)
- ✅ "Set Your Password" heading
- ✅ Password and Confirm Password fields
- ✅ Eye icons to show/hide passwords
- ✅ "Previous" button (gray, left side)
- ✅ "Create Account" button (gradient, right side)
- ❌ Step 1 and Step 2 fields are hidden

### 7. Test Navigation
Click "Previous" button:
- ✅ Should go back to Step 2
- ✅ Your filled data should still be there
- ✅ Progress bar updates to 67%

Click "Previous" again:
- ✅ Should go back to Step 1
- ✅ Your filled data should still be there
- ✅ Progress bar updates to 33%

Navigate forward again to Step 3

### 8. Complete Registration
Fill in passwords:
- Password: `TestPassword123!`
- Confirm Password: `TestPassword123!`

Click "Create Account" button:
- ✅ Button shows loading spinner
- ✅ Button text changes to "Creating Account..."
- ✅ Form submits to server

## Troubleshooting

### Issue: Steps don't change when clicking "Next"
**Possible Causes:**
1. Alpine.js not loaded
2. JavaScript error in console

**Solutions:**
1. Open browser console (F12)
2. Check for errors
3. Verify Alpine.js is loaded: Look for `<script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>` in page source
4. Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

### Issue: Progress bar doesn't update
**Solution:**
- Check browser console for JavaScript errors
- Ensure Alpine.js is loaded
- Try different browser

### Issue: All steps show at once
**Solution:**
- Clear browser cache
- Hard refresh the page
- Check if `x-show="step === 1"` attributes are present in HTML

### Issue: Form stays in loading state
**Solution:**
- This is expected if there are validation errors
- Page will reload and show errors
- Loading state resets on page reload

### Issue: Student fields don't show
**Solution:**
- Ensure "Student" is selected in Account Type dropdown
- Check if `x-show="userType === 'student'"` is working
- Try selecting a different account type, then back to Student

## Expected Behavior

### ✅ Correct Behavior
- Only one step visible at a time
- Progress bar updates when navigating
- "Previous" button works on Steps 2 and 3
- "Next" button works on Steps 1 and 2
- Form data persists when navigating between steps
- Student fields only show when "Student" is selected
- Loading spinner shows on submit
- Validation errors display on correct step

### ❌ Incorrect Behavior
- All steps visible at once → Alpine.js not working
- Can't navigate between steps → JavaScript error
- Progress bar stuck → Alpine.js issue
- Form submits from Step 1 → Missing type="button" on Next buttons
- Infinite loading → Form submission issue (should reload page)

## Browser Console Commands

To debug, open console (F12) and try:

```javascript
// Check if Alpine is loaded
console.log(typeof Alpine);  // Should show "object"

// Check current step (won't work, just for reference)
// The step is managed internally by Alpine
```

## Validation Testing

### Test Required Fields
1. Try clicking "Next" on Step 1 without filling fields
   - Browser should show "Please fill out this field"
   
2. Try submitting on Step 3 without passwords
   - Browser should show "Please fill out this field"

### Test Student-Specific Validation
1. Select "Student" account type
2. Navigate to Step 2
3. Leave Student ID, Campus, or Year Level empty
4. Navigate to Step 3 and submit
5. Page should reload with validation errors

### Test Password Validation
1. Enter mismatched passwords
2. Submit form
3. Should show "Passwords don't match" error

## Success Indicators

When registration works correctly:
1. ✅ Can navigate through all 3 steps
2. ✅ Progress bar updates smoothly
3. ✅ Form data persists between steps
4. ✅ Student fields show/hide based on account type
5. ✅ Submit button shows loading state
6. ✅ Validation errors display correctly
7. ✅ Successful registration redirects to login or dashboard

## Next Steps After Registration

After successful registration:
1. User is redirected to login page
2. Success message appears
3. User can log in with new credentials
4. Student users see their campus in profile
5. Admin can filter by campus in approval views

---

**Need Help?**
- Check browser console for errors
- Verify Alpine.js is loaded
- Try different browser
- Clear cache and cookies
- Check `REGISTRATION_IMPROVEMENTS.md` for technical details
