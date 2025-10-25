"""
Admin final approval views for two-tier approval system.
OSAS staff recommend approval/rejection, Admin makes final decision.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Application, Notification


@login_required
def admin_pending_approvals(request):
    """Admin view to see applications recommended by OSAS staff for final decision."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    # Get applications that OSAS has recommended (approved or rejected)
    applications = Application.objects.filter(
        status__in=['osas_approved', 'osas_rejected']
    ).select_related('student', 'scholarship', 'reviewed_by').order_by('reviewed_at')
    
    # Filter by OSAS recommendation
    recommendation_filter = request.GET.get('recommendation', 'all')
    if recommendation_filter == 'approved':
        applications = applications.filter(status='osas_approved')
    elif recommendation_filter == 'rejected':
        applications = applications.filter(status='osas_rejected')
    
    # Filter by scholarship
    scholarship_filter = request.GET.get('scholarship')
    if scholarship_filter:
        applications = applications.filter(scholarship_id=scholarship_filter)
    
    # Search by student name
    search_query = request.GET.get('search', '')
    if search_query:
        applications = applications.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Counts for filter tabs
    recommendation_counts = {
        'all': Application.objects.filter(status__in=['osas_approved', 'osas_rejected']).count(),
        'approved': Application.objects.filter(status='osas_approved').count(),
        'rejected': Application.objects.filter(status='osas_rejected').count(),
    }
    
    # Get scholarships for filter
    from .models import Scholarship
    scholarships_for_filter = Scholarship.objects.filter(
        applications__status__in=['osas_approved', 'osas_rejected']
    ).distinct().order_by('title')
    
    context = {
        'page_obj': page_obj,
        'recommendation_filter': recommendation_filter,
        'scholarship_filter': scholarship_filter,
        'search_query': search_query,
        'recommendation_counts': recommendation_counts,
        'scholarships_for_filter': scholarships_for_filter,
    }
    
    return render(request, 'admin/pending_approvals.html', context)


@login_required
def admin_final_decision(request, application_id):
    """Admin makes final decision on OSAS-recommended application."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    application = get_object_or_404(
        Application.objects.select_related('student', 'scholarship', 'reviewed_by'),
        id=application_id
    )
    
    # Only allow final decision on OSAS-recommended applications
    if application.status not in ['osas_approved', 'osas_rejected']:
        messages.error(request, 'This application has not been reviewed by OSAS staff yet.')
        return redirect('core:admin_pending_approvals')
    
    if request.method == 'POST':
        decision = request.POST.get('decision')
        comments = request.POST.get('final_comments', '')
        
        if decision in ['approve', 'reject']:
            # Set final decision
            if decision == 'approve':
                # Check if scholarship still has available slots
                if application.scholarship.available_slots_remaining > 0:
                    application.status = 'approved'
                    application.final_decision_by = request.user
                    application.final_decision_at = timezone.now()
                    application.final_decision_comments = comments
                    application.save()
                    
                    messages.success(request, f'Application approved for {application.student.get_full_name()}.')
                    
                    # Create notification for student
                    Notification.objects.create(
                        recipient=application.student,
                        title='Scholarship Application Approved!',
                        message=f'Congratulations! Your application for {application.scholarship.title} has been approved by the administrator.',
                        notification_type='success',
                        related_application=application
                    )
                    
                    # Notify OSAS staff who reviewed it
                    if application.reviewed_by:
                        Notification.objects.create(
                            recipient=application.reviewed_by,
                            title='Application Approved by Admin',
                            message=f'The application you recommended for {application.scholarship.title} has been approved by {request.user.get_full_name()}.',
                            notification_type='success',
                            related_application=application
                        )
                else:
                    messages.error(request, 'Cannot approve - no more slots available for this scholarship.')
                    return redirect('core:admin_final_decision', application_id=application_id)
                    
            elif decision == 'reject':
                application.status = 'rejected'
                application.final_decision_by = request.user
                application.final_decision_at = timezone.now()
                application.final_decision_comments = comments
                application.save()
                
                messages.success(request, f'Application rejected for {application.student.get_full_name()}.')
                
                # Create notification for student
                Notification.objects.create(
                    recipient=application.student,
                    title='Scholarship Application Decision',
                    message=f'Your application for {application.scholarship.title} has been reviewed.',
                    notification_type='info',
                    related_application=application
                )
                
                # Notify OSAS staff who reviewed it
                if application.reviewed_by:
                    Notification.objects.create(
                        recipient=application.reviewed_by,
                        title='Application Rejected by Admin',
                        message=f'The application you reviewed for {application.scholarship.title} has been rejected by {request.user.get_full_name()}.',
                        notification_type='info',
                        related_application=application
                    )
            
            return redirect('core:admin_pending_approvals')
    
    # Get student's other applications for context
    student_other_apps = Application.objects.filter(
        student=application.student
    ).exclude(id=application.id).select_related('scholarship')
    
    # Get application documents
    documents = application.documents.all()
    
    context = {
        'application': application,
        'student_other_apps': student_other_apps,
        'documents': documents,
    }
    
    return render(request, 'admin/final_decision.html', context)


@login_required
def admin_review_history(request):
    """Admin view to see history of all final decisions made."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    # Get applications with final decisions
    applications = Application.objects.filter(
        final_decision_by__isnull=False
    ).select_related(
        'student', 'scholarship', 'reviewed_by', 'final_decision_by'
    ).order_by('-final_decision_at')
    
    # Filter by decision
    decision_filter = request.GET.get('decision', 'all')
    if decision_filter == 'approved':
        applications = applications.filter(status='approved')
    elif decision_filter == 'rejected':
        applications = applications.filter(status='rejected')
    
    # Filter by admin who made decision
    admin_filter = request.GET.get('admin')
    if admin_filter == 'me':
        applications = applications.filter(final_decision_by=request.user)
    
    # Pagination
    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Counts
    decision_counts = {
        'all': Application.objects.filter(final_decision_by__isnull=False).count(),
        'approved': Application.objects.filter(status='approved', final_decision_by__isnull=False).count(),
        'rejected': Application.objects.filter(status='rejected', final_decision_by__isnull=False).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'decision_filter': decision_filter,
        'admin_filter': admin_filter,
        'decision_counts': decision_counts,
    }
    
    return render(request, 'admin/review_history.html', context)
