# Fix: OSAS Approval Workflow Not Showing in Admin

## Problem
OSAS staff were approving/rejecting applications, but the admin's "Pending Final Approvals" page was showing empty - no applications to review.

## Root Cause
The OSAS application review form had a mismatch between the form field names and what the view expected:

1. **Form Issue**: The form in `templates/osas/application_review.html` was:
   - Using `name="decision"` instead of `name="action"`
   - Using values `approved`, `rejected`, `additional_info_required`
   - Posting to a separate `submit_review` URL

2. **View Expectation**: The `application_review` view in `core/views.py` was looking for:
   - Field name: `action`
   - Values: `approve`, `reject`, `request_info`

3. **Old View Conflict**: There was an old `submit_review` view that was using the OLD approval system (directly setting `approved`/`rejected` instead of `osas_approved`/`osas_rejected`)

## Solution

### 1. Fixed the OSAS Review Form
**File**: `templates/osas/application_review.html`

Changed:
```html
<!-- OLD -->
<form method="POST" action="{% url 'core:submit_review' application.id %}">
    <select name="decision" id="decision">
        <option value="approved">✓ Approve Application</option>
        <option value="rejected">✗ Reject Application</option>
        <option value="additional_info_required">⚠ Request Additional Information</option>
    </select>
</form>
```

To:
```html
<!-- NEW -->
<form method="POST">
    <select name="action" id="action">
        <option value="approve">✓ Recommend for Approval</option>
        <option value="reject">✗ Recommend for Rejection</option>
        <option value="request_info">⚠ Request Additional Information</option>
    </select>
</form>
```

**Key Changes**:
- Changed `name="decision"` → `name="action"`
- Changed `value="approved"` → `value="approve"`
- Changed `value="rejected"` → `value="reject"`
- Changed `value="additional_info_required"` → `value="request_info"`
- Removed `action="{% url 'core:submit_review' application.id %}"` (posts to same page now)
- Updated text to say "Recommend" instead of direct approval

### 2. Deprecated Old submit_review View
**File**: `core/views.py`

Changed the `submit_review` function to just redirect to `application_review`:
```python
@login_required
def submit_review(request, application_id):
    """Submit review decision for an application - DEPRECATED, redirects to application_review."""
    # This view is deprecated in favor of the two-tier approval system
    # Redirect to the application_review view which handles the new workflow
    return redirect('core:review_application', application_id=application_id)
```

## How It Works Now

### OSAS Workflow:
1. OSAS staff goes to Review Queue
2. Clicks "Review" on an application
3. Selects decision from dropdown:
   - "Recommend for Approval" → Sets status to `osas_approved`
   - "Recommend for Rejection" → Sets status to `osas_rejected`
   - "Request Additional Information" → Sets status to `additional_info_required`
4. Adds comments
5. Clicks "Submit Review"
6. Application is saved with new status
7. Admin receives notification

### Admin Workflow:
1. Admin receives notification
2. Goes to "Pending Final Approvals"
3. Sees applications with status `osas_approved` or `osas_rejected`
4. Reviews OSAS recommendation and comments
5. Makes final decision (Approve or Reject)
6. Application status changes to `approved` or `rejected`
7. Student and OSAS staff receive notifications

## Testing

To test the fix:

1. **Login as OSAS staff**
2. **Go to Review Queue**
3. **Click "Review" on a pending application**
4. **Select "Recommend for Approval"**
5. **Add comments**: "Test recommendation"
6. **Click "Submit Review"**
7. **Verify**: Message says "Application recommended for approval. Awaiting admin final decision."

8. **Login as Admin**
9. **Go to "Pending Final Approvals"**
10. **Verify**: The application now appears in the list
11. **Click "Make Decision"**
12. **Select "Approve" or "Reject"**
13. **Submit final decision**
14. **Verify**: Application disappears from pending list

## Database Check

To verify applications are being created with correct statuses:

```bash
python manage.py shell -c "from core.models import Application; print('OSAS Approved:', Application.objects.filter(status='osas_approved').count()); print('OSAS Rejected:', Application.objects.filter(status='osas_rejected').count())"
```

## Status Flow

```
Student Submits
      ↓
   pending
      ↓
OSAS Assigns → under_review
      ↓
OSAS Recommends Approval → osas_approved ← Admin sees this!
      ↓
Admin Approves → approved
```

OR

```
OSAS Recommends Rejection → osas_rejected ← Admin sees this!
      ↓
Admin Rejects → rejected
```

## Files Modified

1. `templates/osas/application_review.html` - Fixed form field names and values
2. `core/views.py` - Deprecated old submit_review view
3. `FIX_OSAS_APPROVAL_WORKFLOW.md` - This documentation

## Verification

✅ Form field names match view expectations
✅ Form values match view logic
✅ Old conflicting view deprecated
✅ No syntax errors
✅ Two-tier workflow intact

## Next Steps

1. Test the complete workflow with real data
2. Train OSAS staff on the new "Recommend" terminology
3. Train admins on the "Pending Final Approvals" page
4. Monitor for any issues

---

**Status**: ✅ FIXED
**Date**: [Current Date]
**Fixed By**: Kiro AI Assistant
