# Two-Tier Approval Workflow Diagram

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         STUDENT PORTAL                          │
│                                                                 │
│  Student fills application form                                │
│  • Personal statement                                          │
│  • GPA                                                         │
│  • Upload documents                                            │
│  • Submit                                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Status: PENDING
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OSAS STAFF REVIEW (Tier 1)                   │
│                                                                 │
│  OSAS staff member:                                            │
│  1. Assigns application to self                                │
│  2. Reviews all documents                                      │
│  3. Checks eligibility criteria                                │
│  4. Evaluates qualifications                                   │
│  5. Adds detailed comments                                     │
│                                                                 │
│  Status: UNDER_REVIEW                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ OSAS Decision
                         ▼
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌──────────────────┐           ┌──────────────────┐
│  OSAS Recommends │           │  OSAS Recommends │
│    APPROVAL      │           │    REJECTION     │
│                  │           │                  │
│ Status:          │           │ Status:          │
│ OSAS_APPROVED    │           │ OSAS_REJECTED    │
└────────┬─────────┘           └────────┬─────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                         │ Notification sent to Admin
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ADMIN FINAL DECISION (Tier 2)                 │
│                                                                 │
│  Admin reviews:                                                │
│  • Full application details                                    │
│  • OSAS recommendation                                         │
│  • OSAS comments                                               │
│  • All documents                                               │
│  • Scholarship availability                                    │
│  • Student's other applications                                │
│                                                                 │
│  Admin can:                                                    │
│  • Agree with OSAS recommendation                              │
│  • Override OSAS recommendation                                │
│  • Add final decision comments                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Admin Decision
                         ▼
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌──────────────────┐           ┌──────────────────┐
│  Admin APPROVES  │           │  Admin REJECTS   │
│                  │           │                  │
│ Status:          │           │ Status:          │
│ APPROVED         │           │ REJECTED         │
│                  │           │                  │
│ ✅ Student gets  │           │ ❌ Student does  │
│    scholarship   │           │    not get it    │
└────────┬─────────┘           └────────┬─────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                         │ Notifications sent
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        NOTIFICATIONS                            │
│                                                                 │
│  📧 Student receives:                                          │
│     • Final decision notification                              │
│     • Status update in dashboard                               │
│                                                                 │
│  📧 OSAS staff receives:                                       │
│     • Admin decision notification                              │
│     • Feedback on their recommendation                         │
└─────────────────────────────────────────────────────────────────┘
```

## Status Progression

```
PENDING
   ↓
   │ OSAS assigns to self
   ↓
UNDER_REVIEW
   ↓
   │ OSAS makes recommendation
   ↓
OSAS_APPROVED  or  OSAS_REJECTED
   ↓                    ↓
   │ Admin reviews      │
   ↓                    ↓
APPROVED  or  REJECTED
```

## Decision Matrix

```
┌─────────────────────┬──────────────┬──────────────┐
│ OSAS Recommendation │ Admin Action │ Final Result │
├─────────────────────┼──────────────┼──────────────┤
│ Approve             │ Approve      │ ✅ APPROVED  │
│ Approve             │ Reject       │ ❌ REJECTED  │
│ Reject              │ Approve      │ ✅ APPROVED  │
│ Reject              │ Reject       │ ❌ REJECTED  │
└─────────────────────┴──────────────┴──────────────┘
```

## User Permissions

```
┌──────────────┬─────────────┬─────────────┬─────────────┐
│ Action       │ Student     │ OSAS Staff  │ Admin       │
├──────────────┼─────────────┼─────────────┼─────────────┤
│ Submit App   │ ✅ Yes      │ ❌ No       │ ❌ No       │
│ Review App   │ ❌ No       │ ✅ Yes      │ ✅ Yes      │
│ Recommend    │ ❌ No       │ ✅ Yes      │ ❌ No       │
│ Final Decide │ ❌ No       │ ❌ No       │ ✅ Yes      │
│ View History │ Own only    │ Own reviews │ All         │
└──────────────┴─────────────┴─────────────┴─────────────┘
```

## Page Flow for Admin

```
Admin Dashboard
       │
       ├─→ Pending Final Approvals
       │         │
       │         ├─→ Filter by recommendation
       │         ├─→ Search by student
       │         ├─→ Filter by scholarship
       │         │
       │         └─→ Click "Make Decision"
       │                   │
       │                   ▼
       │         Final Decision Page
       │                   │
       │                   ├─→ Review application
       │                   ├─→ Review OSAS comments
       │                   ├─→ View documents
       │                   ├─→ Choose approve/reject
       │                   ├─→ Add comments
       │                   │
       │                   └─→ Submit Decision
       │                             │
       │                             ▼
       │                   Notifications Sent
       │
       └─→ Decision History
                 │
                 ├─→ View all decisions
                 ├─→ Filter by type
                 └─→ Filter by admin
```

## Page Flow for OSAS

```
OSAS Dashboard
       │
       └─→ Review Queue
                 │
                 ├─→ Filter by status
                 ├─→ Filter by scholarship
                 │
                 └─→ Click on Application
                           │
                           ▼
                 Application Review Page
                           │
                           ├─→ Review details
                           ├─→ View documents
                           ├─→ Add comments
                           │
                           └─→ Make Recommendation
                                     │
                                     ├─→ Approve (recommend)
                                     ├─→ Reject (recommend)
                                     └─→ Request Info
                                           │
                                           ▼
                                 Admin Notified
```

## Timeline Example

```
Day 1, 9:00 AM  │ Student submits application
                │ Status: PENDING
                │
Day 1, 2:00 PM  │ OSAS staff assigns to self
                │ Status: UNDER_REVIEW
                │
Day 2, 10:00 AM │ OSAS staff recommends approval
                │ Status: OSAS_APPROVED
                │ Admin receives notification
                │
Day 2, 3:00 PM  │ Admin reviews application
                │
Day 2, 3:30 PM  │ Admin approves application
                │ Status: APPROVED
                │ Student & OSAS notified
                │
Day 2, 3:31 PM  │ ✅ Process complete!
```

## Audit Trail

Every application has a complete audit trail:

```
┌─────────────────────────────────────────────────────┐
│ Application #12345                                  │
├─────────────────────────────────────────────────────┤
│ Submitted by: John Doe                              │
│ Submitted at: 2024-01-15 09:00:00                   │
│                                                     │
│ Reviewed by: Jane Smith (OSAS)                      │
│ Reviewed at: 2024-01-16 10:00:00                    │
│ OSAS Status: OSAS_APPROVED                          │
│ OSAS Comments: "Strong candidate, all docs valid"   │
│                                                     │
│ Final Decision by: Bob Admin                        │
│ Final Decision at: 2024-01-16 15:30:00              │
│ Final Status: APPROVED                              │
│ Admin Comments: "Agreed with OSAS recommendation"   │
└─────────────────────────────────────────────────────┘
```

## Benefits Visualization

```
┌─────────────────────────────────────────────────────┐
│              TWO-TIER APPROVAL BENEFITS             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🎯 Quality Control                                 │
│     Two sets of eyes on every application           │
│                                                     │
│  📊 Accountability                                  │
│     Clear responsibility at each stage              │
│                                                     │
│  📝 Audit Trail                                     │
│     Complete record of all decisions                │
│                                                     │
│  🔔 Transparency                                    │
│     All parties informed at each step               │
│                                                     │
│  ⚖️ Fairness                                        │
│     Consistent review process                       │
│                                                     │
│  🛡️ Oversight                                       │
│     Admin can override if needed                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```
