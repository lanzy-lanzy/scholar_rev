# Admin Final Approval Guide

## Quick Start for Administrators

### Accessing Pending Approvals

1. **From Dashboard**: Click the "Pending Final Approvals" button (teal colored)
2. **Direct URL**: `/dashboard/admin/pending-approvals/`

### Making a Final Decision

#### Step 1: Review the List
- View all applications recommended by OSAS staff
- Filter by:
  - **All Pending**: See both approved and rejected recommendations
  - **OSAS Recommended Approval**: Only see applications OSAS wants to approve
  - **OSAS Recommended Rejection**: Only see applications OSAS wants to reject
- Use search to find specific students
- Filter by scholarship

#### Step 2: Click "Make Decision"
- Click the "Make Decision" button on any application
- You'll see:
  - Full application details
  - Student's personal statement
  - GPA and other info
  - OSAS staff recommendation
  - OSAS comments explaining their decision
  - All submitted documents
  - Scholarship availability info

#### Step 3: Make Your Decision
Choose one of two options:
- **Approve Application**: Final approval, student gets the scholarship
- **Reject Application**: Final rejection, student is notified

Add optional comments explaining your decision.

#### Step 4: Submit
- Click "Submit Final Decision"
- Notifications are automatically sent to:
  - The student
  - The OSAS staff member who reviewed it

### Important Notes

⚠️ **Scholarship Slots**: The system checks if slots are available before allowing approval. If no slots remain, you'll see an error.

⚠️ **Cannot Undo**: Once you make a final decision, it's recorded permanently in the system. Review carefully!

✅ **Audit Trail**: All your decisions are logged with timestamp and comments in the Decision History.

### Viewing Decision History

1. Click "Decision History" from the dashboard
2. See all final decisions made by all admins
3. Filter by:
   - All decisions
   - Approved only
   - Rejected only
   - Your decisions only

### Workflow Summary

```
Student Submits Application
         ↓
OSAS Staff Reviews
         ↓
OSAS Recommends (Approve/Reject)
         ↓
Admin Receives Notification
         ↓
Admin Reviews Recommendation
         ↓
Admin Makes Final Decision
         ↓
Student & OSAS Notified
```

### Status Meanings

| Status Badge | Meaning | Action Needed |
|--------------|---------|---------------|
| 🟡 Pending Review | Waiting for OSAS | None (OSAS handles) |
| 🔵 Under Review | OSAS is reviewing | None (OSAS handles) |
| 🟢 OSAS Recommended Approval | OSAS says approve | **You decide** |
| 🟣 OSAS Recommended Rejection | OSAS says reject | **You decide** |
| ✅ Approved by Admin | You approved it | Complete |
| ❌ Rejected by Admin | You rejected it | Complete |
| 🟠 Additional Info Required | Student needs to provide more | Wait for student |

### Best Practices

1. **Review OSAS Comments**: They often contain important context
2. **Check Documents**: Verify all required documents are submitted
3. **Consider Slots**: Check how many slots remain for the scholarship
4. **Add Comments**: Explain your reasoning for future reference
5. **Be Timely**: Students are waiting for decisions
6. **Check History**: Review student's other applications if relevant

### Common Scenarios

#### Scenario 1: OSAS Recommends Approval, You Agree
✅ Simply approve with optional comments like "Agreed with OSAS recommendation"

#### Scenario 2: OSAS Recommends Approval, You Disagree
❌ Reject with detailed comments explaining why you disagree

#### Scenario 3: OSAS Recommends Rejection, You Disagree
✅ Approve with comments explaining your reasoning

#### Scenario 4: No Slots Available
⚠️ System will prevent approval automatically. Consider:
- Rejecting with explanation about slots
- Checking if you can increase scholarship slots
- Putting on waitlist (if implemented)

### Keyboard Shortcuts

- **Tab**: Navigate between form fields
- **Enter**: Submit form (when focused on submit button)
- **Esc**: Cancel (browser back)

### Troubleshooting

**Q: I don't see any pending approvals**
- Check if OSAS has reviewed any applications yet
- Verify you're logged in as an admin
- Check the filter tabs (might be filtered)

**Q: Can't approve an application**
- Check if scholarship slots are full
- Verify the application status is `osas_approved` or `osas_rejected`
- Check if you have admin permissions

**Q: Made a mistake in my decision**
- Contact system administrator
- Decisions are permanent and require database access to change
- This is by design for audit trail integrity

### Support

For technical issues or questions:
- Contact OSAS staff for application-related questions
- Contact IT support for system issues
- Check the Decision History for past precedents
