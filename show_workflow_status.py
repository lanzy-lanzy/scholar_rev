"""
Display the complete workflow status for all applications
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from core.models import Application, User
from django.utils import timezone

def get_status_emoji(status):
    """Return emoji for status"""
    emojis = {
        'pending': '⏳',
        'under_review': '👀',
        'osas_approved': '✅',
        'osas_rejected': '❌',
        'approved': '🎉',
        'rejected': '⛔',
        'additional_info_required': '📝'
    }
    return emojis.get(status, '❓')

print("\n" + "=" * 80)
print("SCHOLARSHIP APPLICATION WORKFLOW STATUS")
print("=" * 80)

# Get all applications
all_apps = Application.objects.all().select_related(
    'student', 'scholarship', 'reviewed_by', 'final_decision_by'
).order_by('status', 'submitted_at')

if all_apps.count() == 0:
    print("\nNo applications found in the system.")
    exit()

# Group by status
status_groups = {}
for app in all_apps:
    status = app.status
    if status not in status_groups:
        status_groups[status] = []
    status_groups[status].append(app)

# Display by workflow stage
print("\n📋 WORKFLOW STAGES:")
print("-" * 80)

# Stage 1: Pending OSAS Review
pending = status_groups.get('pending', [])
print(f"\n1️⃣  PENDING OSAS REVIEW ({len(pending)} applications)")
if pending:
    for app in pending:
        print(f"   ⏳ {app.student.get_full_name()} → {app.scholarship.title}")
        print(f"      Submitted: {app.submitted_at.strftime('%Y-%m-%d %H:%M')}")
else:
    print("   ✓ No applications pending")

# Stage 2: Under Review by OSAS
under_review = status_groups.get('under_review', [])
print(f"\n2️⃣  UNDER REVIEW BY OSAS ({len(under_review)} applications)")
if under_review:
    for app in under_review:
        print(f"   👀 {app.student.get_full_name()} → {app.scholarship.title}")
        print(f"      Assigned to: {app.reviewed_by.get_full_name() if app.reviewed_by else 'Unassigned'}")
        print(f"      ⚠️  ACTION NEEDED: OSAS must complete review and submit recommendation")
else:
    print("   ✓ No applications under review")

# Stage 3: Awaiting Admin Decision
osas_approved = status_groups.get('osas_approved', [])
osas_rejected = status_groups.get('osas_rejected', [])
awaiting_admin = osas_approved + osas_rejected
print(f"\n3️⃣  AWAITING ADMIN FINAL DECISION ({len(awaiting_admin)} applications)")
if awaiting_admin:
    for app in awaiting_admin:
        emoji = '✅' if app.status == 'osas_approved' else '❌'
        recommendation = 'APPROVAL' if app.status == 'osas_approved' else 'REJECTION'
        print(f"   {emoji} {app.student.get_full_name()} → {app.scholarship.title}")
        print(f"      OSAS Recommendation: {recommendation}")
        print(f"      Reviewed by: {app.reviewed_by.get_full_name()}")
        print(f"      Reviewed at: {app.reviewed_at.strftime('%Y-%m-%d %H:%M')}")
        if app.reviewer_comments:
            print(f"      Comments: {app.reviewer_comments[:100]}...")
        print(f"      ⚠️  ACTION NEEDED: Admin must make final decision")
        print()
else:
    print("   ✓ No applications awaiting admin decision")

# Stage 4: Final Decisions Made
approved = status_groups.get('approved', [])
rejected = status_groups.get('rejected', [])
completed = approved + rejected
print(f"\n4️⃣  COMPLETED ({len(completed)} applications)")
if completed:
    for app in completed:
        emoji = '🎉' if app.status == 'approved' else '⛔'
        decision = 'APPROVED' if app.status == 'approved' else 'REJECTED'
        print(f"   {emoji} {app.student.get_full_name()} → {app.scholarship.title}")
        print(f"      Final Decision: {decision}")
        if app.final_decision_by:
            print(f"      Decided by: {app.final_decision_by.get_full_name()}")
            print(f"      Decided at: {app.final_decision_at.strftime('%Y-%m-%d %H:%M')}")
else:
    print("   ✓ No completed applications")

# Additional Info Required
additional_info = status_groups.get('additional_info_required', [])
if additional_info:
    print(f"\n📝 ADDITIONAL INFO REQUIRED ({len(additional_info)} applications)")
    for app in additional_info:
        print(f"   📝 {app.student.get_full_name()} → {app.scholarship.title}")
        print(f"      Requested by: {app.reviewed_by.get_full_name() if app.reviewed_by else 'Unknown'}")
        print(f"      ⚠️  ACTION NEEDED: Student must provide additional information")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Applications: {all_apps.count()}")
print(f"  • Pending OSAS Review: {len(pending)}")
print(f"  • Under OSAS Review: {len(under_review)}")
print(f"  • Awaiting Admin Decision: {len(awaiting_admin)}")
print(f"  • Completed: {len(completed)}")
if additional_info:
    print(f"  • Additional Info Required: {len(additional_info)}")

# Action Items
print("\n" + "=" * 80)
print("ACTION ITEMS")
print("=" * 80)

action_count = 0

if pending:
    print(f"\n✓ OSAS: Review {len(pending)} pending application(s)")
    action_count += len(pending)

if under_review:
    print(f"\n✓ OSAS: Complete review for {len(under_review)} application(s) under review")
    print("   (Submit recommendation: approve/reject/request info)")
    action_count += len(under_review)

if awaiting_admin:
    print(f"\n✓ ADMIN: Make final decision on {len(awaiting_admin)} OSAS-recommended application(s)")
    print("   Navigate to: Dashboard > Pending Final Approvals")
    action_count += len(awaiting_admin)

if additional_info:
    print(f"\n✓ STUDENTS: Provide additional information for {len(additional_info)} application(s)")
    action_count += len(additional_info)

if action_count == 0:
    print("\n✓ No pending actions - all applications are completed!")

print("\n" + "=" * 80)
