# Testing Guide - Two-Tier Approval System

## Quick Test Workflow

### Prerequisites
- OSAS staff account
- Admin account
- Student account with at least one application

### Test 1: OSAS Recommendation

1. **Login as OSAS staff**
   - URL: `/auth/login/`
   - Use OSAS credentials

2. **Navigate to Review Queue**
   - Click "Review Queue" from dashboard
   - OR go to: `/review-queue/`

3. **Select an Application**
   - Find a "Pending" application
   - Click "Assign to Me" (if not already assigned)
   - Click "Review"

4. **Make Recommendation**
   - Select "Recommend for Approval" from dropdown
   - Add comments: "Test: Strong candidate, all requirements met"
   - Click "Submit Review"

5. **Verify Success**
   - ✅ Should see message: "Application recommended for approval. Awaiting admin final decision."
   - ✅ Should redirect to Review Queue
   - ✅ Application should show status "OSAS Recommended for Approval"

### Test 2: Admin Final Decision

1. **Login as Admin**
   - URL: `/auth/login/`
   - Use admin credentials

2. **Check Notifications**
   - ✅ Should see notification: "New Application Recommended for Approval"

3. **Navigate to Pending Approvals**
   - Click "Pending Final Approvals" button (teal colored)
   - OR go to: `/dashboard/admin/pending-approvals/`

4. **Verify Application Appears**
   - ✅ Should see the application in the list
   - ✅ Should see OSAS recommendation badge
   - ✅ Should see OSAS comments

5. **Make Final Decision**
   - Click "Make Decision" button
   - Review all details
   - Select "Approve Application"
   - Add comments: "Test: Approved based on OSAS recommendation"
   - Click "Submit Final Decision"

6. **Verify Success**
   - ✅ Should see message: "Application approved for [Student Name]"
   - ✅ Should redirect to Pending Approvals
   - ✅ Application should disappear from list

### Test 3: Verify Notifications

1. **Login as Student**
   - Check notifications
   - ✅ Should see: "Scholarship Application Approved!"

2. **Login as OSAS Staff**
   - Check notifications
   - ✅ Should see: "Application Approved by Admin"

### Test 4: Rejection Workflow

Repeat Test 1 and Test 2, but:
- OSAS: Select "Recommend for Rejection"
- Admin: Select "Reject Application"

### Test 5: Database Verification

Run this command to check statuses:
```bash
python manage.py shell -c "from core.models import Application; print('OSAS Approved:', Application.objects.filter(status='osas_approved').count()); print('OSAS Rejected:', Application.objects.filter(status='osas_rejected').count()); print('Final Approved:', Application.objects.filter(status='approved', final_decision_by__isnull=False).count()); print('Final Rejected:', Application.objects.filter(status='rejected', final_decision_by__isnull=False).count())"
```

Expected output after tests:
```
OSAS Approved: 0 (should be 0 after admin decides)
OSAS Rejected: 0 (should be 0 after admin decides)
Final Approved: 1 (or more)
Final Rejected: 1 (or more)
```

## Detailed Test Cases

### Test Case 1: OSAS Recommends Approval → Admin Approves

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | OSAS reviews application | Status: `under_review` |
| 2 | OSAS selects "Recommend for Approval" | Status: `osas_approved` |
| 3 | Admin receives notification | Notification appears |
| 4 | Admin views pending approvals | Application appears in list |
| 5 | Admin approves | Status: `approved` |
| 6 | Student receives notification | "Application Approved!" |
| 7 | OSAS receives notification | "Application Approved by Admin" |

### Test Case 2: OSAS Recommends Approval → Admin Rejects

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | OSAS reviews application | Status: `under_review` |
| 2 | OSAS selects "Recommend for Approval" | Status: `osas_approved` |
| 3 | Admin receives notification | Notification appears |
| 4 | Admin views pending approvals | Application appears in list |
| 5 | Admin rejects (overrides OSAS) | Status: `rejected` |
| 6 | Student receives notification | "Application Decision" |
| 7 | OSAS receives notification | "Application Rejected by Admin" |

### Test Case 3: OSAS Recommends Rejection → Admin Approves

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | OSAS reviews application | Status: `under_review` |
| 2 | OSAS selects "Recommend for Rejection" | Status: `osas_rejected` |
| 3 | Admin receives notification | Notification appears |
| 4 | Admin views pending approvals | Application appears in list |
| 5 | Admin approves (overrides OSAS) | Status: `approved` |
| 6 | Student receives notification | "Application Approved!" |
| 7 | OSAS receives notification | "Application Approved by Admin" |

### Test Case 4: OSAS Recommends Rejection → Admin Rejects

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | OSAS reviews application | Status: `under_review` |
| 2 | OSAS selects "Recommend for Rejection" | Status: `osas_rejected` |
| 3 | Admin receives notification | Notification appears |
| 4 | Admin views pending approvals | Application appears in list |
| 5 | Admin rejects | Status: `rejected` |
| 6 | Student receives notification | "Application Decision" |
| 7 | OSAS receives notification | "Application Rejected by Admin" |

### Test Case 5: Request Additional Information

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | OSAS reviews application | Status: `under_review` |
| 2 | OSAS selects "Request Additional Information" | Status: `additional_info_required` |
| 3 | Student receives notification | "Additional Information Required" |
| 4 | Application does NOT appear in admin pending | Not in admin queue |

## Filter Testing

### Test Pending Approvals Filters

1. **Filter by Recommendation Type**
   - Click "All Pending" tab → Should show all
   - Click "OSAS Recommended Approval" tab → Should show only `osas_approved`
   - Click "OSAS Recommended Rejection" tab → Should show only `osas_rejected`

2. **Search by Student Name**
   - Enter student name in search box
   - Click "Apply Filters"
   - Should show only matching students

3. **Filter by Scholarship**
   - Select scholarship from dropdown
   - Click "Apply Filters"
   - Should show only applications for that scholarship

4. **Combined Filters**
   - Select recommendation type + scholarship
   - Should show applications matching both criteria

## Edge Cases

### Edge Case 1: No Slots Available
1. Create scholarship with 1 slot
2. OSAS recommends 2 applications for approval
3. Admin approves first application → Success
4. Admin tries to approve second → Should see error: "Cannot approve - no more slots available"

### Edge Case 2: Multiple Admins
1. Admin A views pending approvals
2. Admin B approves an application
3. Admin A tries to approve same application → Should see error or redirect

### Edge Case 3: OSAS Changes Mind
1. OSAS recommends approval
2. OSAS tries to change to rejection → Should not be able to (status already set)
3. Admin must make final decision

## Performance Testing

### Test with Multiple Applications
1. Create 20+ applications
2. Have OSAS recommend all for approval
3. Check admin pending approvals page loads quickly
4. Test pagination works correctly
5. Test filters work with large dataset

## Browser Testing

Test on:
- ✅ Chrome
- ✅ Firefox
- ✅ Edge
- ✅ Safari (if available)
- ✅ Mobile browsers

## Accessibility Testing

- ✅ Keyboard navigation works
- ✅ Screen reader compatible
- ✅ Color contrast sufficient
- ✅ Form labels present

## Security Testing

1. **Permission Checks**
   - Try accessing admin pages as OSAS → Should be denied
   - Try accessing admin pages as student → Should be denied
   - Try accessing OSAS pages as student → Should be denied

2. **CSRF Protection**
   - Forms should have CSRF tokens
   - Submissions without tokens should fail

3. **SQL Injection**
   - Try entering SQL in search fields
   - Should be properly escaped

## Troubleshooting

### Issue: Applications not appearing in admin pending approvals

**Check:**
1. Are applications actually in `osas_approved` or `osas_rejected` status?
   ```bash
   python manage.py shell -c "from core.models import Application; print(Application.objects.filter(status__in=['osas_approved', 'osas_rejected']).count())"
   ```

2. Is the admin logged in correctly?
3. Are there any JavaScript errors in browser console?

### Issue: Form submission not working

**Check:**
1. Browser console for errors
2. Django logs for errors
3. CSRF token present in form
4. Form field names match view expectations

### Issue: Notifications not appearing

**Check:**
1. Notification objects created in database
2. User has correct permissions
3. Notification template rendering correctly

## Success Criteria

✅ OSAS can recommend applications for approval/rejection
✅ Admin receives notifications of OSAS recommendations
✅ Admin can view pending approvals list
✅ Admin can make final decisions
✅ Students receive notifications of final decisions
✅ OSAS receives notifications of admin decisions
✅ All filters work correctly
✅ Pagination works correctly
✅ No errors in browser console
✅ No errors in Django logs
✅ Audit trail complete (all decisions logged)

---

**Testing Status**: Ready for Testing
**Last Updated**: [Current Date]
