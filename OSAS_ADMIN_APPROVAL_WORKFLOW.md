# OSAS-Admin Two-Tier Approval Workflow

## Overview
The scholarship system uses a two-tier approval process:
1. **OSAS Staff** reviews applications and makes recommendations
2. **Admin** makes the final approval/rejection decision

## Workflow Steps

### Step 1: OSAS Review
1. OSAS staff logs in and navigates to **Review Queue**
2. They see all pending applications
3. They can assign an application to themselves (status changes to `under_review`)
4. They review the application details:
   - Student information
   - GPA and academic records
   - Personal statement
   - Supporting documents
5. They make a decision:
   - **Recommend for Approval** → Status: `osas_approved`
   - **Recommend for Rejection** → Status: `osas_rejected`
   - **Request Additional Information** → Status: `additional_info_required`
6. They add comments explaining their recommendation
7. They submit the review

### Step 2: Admin Notification
When OSAS submits a recommendation:
- All admin users receive a notification
- The notification includes:
  - Student name
  - Scholarship title
  - OSAS staff member who reviewed it
  - Recommendation (approval/rejection)

### Step 3: Admin Final Decision
1. Admin logs in and navigates to **Pending Final Approvals**
2. They see all applications with OSAS recommendations
3. They can filter by:
   - Recommendation type (approved/rejected)
   - Campus
   - Scholarship
   - Student name (search)
4. They click "Make Decision" on an application
5. They review:
   - All student information
   - OSAS comments and recommendation
   - Application documents
6. They make the final decision:
   - **Approve** → Status: `approved`
   - **Reject** → Status: `rejected`
7. They add final decision comments
8. They submit the decision

### Step 4: Notifications
After admin makes final decision:
- **Student** receives notification of the decision
- **OSAS staff** who reviewed it receives notification of admin's decision

## Application Status Flow

```
pending
  ↓ (OSAS assigns to self)
under_review
  ↓ (OSAS recommends)
osas_approved OR osas_rejected
  ↓ (Admin decides)
approved OR rejected
```

## Important Notes

### For OSAS Staff:
- You must **complete the review** by selecting a decision (approve/reject/request info)
- Simply assigning to yourself (`under_review`) is not enough
- Your recommendation goes to admins for final decision
- You cannot make final approval/rejection decisions

### For Admins:
- You only see applications that OSAS has recommended
- Applications still `pending` or `under_review` won't appear in Pending Approvals
- You make the final binding decision
- You can see OSAS comments to help inform your decision

## Troubleshooting

### "No pending approvals" message
This means:
- No applications have been recommended by OSAS yet
- All OSAS recommendations have been processed
- Check if there are applications in `under_review` status that need OSAS to complete

### Application not appearing for admin
Check:
1. Has OSAS completed the review? (status should be `osas_approved` or `osas_rejected`)
2. If status is still `under_review`, OSAS needs to submit their decision
3. Run `python check_pending_approvals.py` to see current status

## Database Status Values

| Status | Meaning | Who Can See |
|--------|---------|-------------|
| `pending` | New application, not yet reviewed | OSAS, Admin |
| `under_review` | OSAS assigned to themselves | OSAS, Admin |
| `osas_approved` | OSAS recommends approval | Admin (Pending Approvals) |
| `osas_rejected` | OSAS recommends rejection | Admin (Pending Approvals) |
| `approved` | Admin final approval | All |
| `rejected` | Admin final rejection | All |
| `additional_info_required` | More info needed from student | Student, OSAS, Admin |

## Testing the System

Use the provided scripts:
- `check_pending_approvals.py` - Check current status of all applications
- `test_osas_recommendation.py` - Simulate OSAS recommendation for testing

## URLs

- OSAS Review Queue: `/review-queue/`
- Admin Pending Approvals: `/dashboard/admin/pending-approvals/`
- Admin Final Decision: `/dashboard/admin/final-decision/<application_id>/`
- Admin Review History: `/dashboard/admin/review-history/`
