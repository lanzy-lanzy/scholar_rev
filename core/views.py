from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from django.core.exceptions import ValidationError
from .forms import (
    CustomUserCreationForm,
    UserProfileForm,
    DocumentUploadForm,
    ApplicationForm,
    UserUpdateForm,
    ScholarshipForm,
    DynamicApplicationForm,
    RegistrationStep1Form,
    RegistrationStep2Form,
    RegistrationStudentStep3Form,
)
from .models import Scholarship, Application, Notification, ApplicationDocument, DocumentRequirement


def landing_page(request):
    """Landing page for the scholarship management system."""
    # Get some statistics for the landing page
    from .models import Scholarship, Application
    
    total_scholarships = Scholarship.objects.filter(is_active=True).count()
    total_applications = Application.objects.count()
    
    context = {
        'total_scholarships': total_scholarships,
        'total_applications': total_applications,
    }
    
    return render(request, 'landing.html', context)


def _finalize_registration(request, registration_data):
    """Helper to create the user using the full data collected across steps."""
    # Build a data dict suitable for CustomUserCreationForm
    form_data = {
        'username': registration_data.get('username'),
        'email': registration_data.get('email'),
        'password1': registration_data.get('password1'),
        'password2': registration_data.get('password2'),
        'first_name': registration_data.get('first_name'),
        'last_name': registration_data.get('last_name'),
        'user_type': registration_data.get('user_type'),
        'student_id': registration_data.get('student_id'),
        'campus': registration_data.get('campus'),
        'year_level': registration_data.get('year_level'),
        'department': registration_data.get('department'),
        'phone_number': registration_data.get('phone_number'),
    }

    form = CustomUserCreationForm(form_data)
    if form.is_valid():
        user = form.save()
        login(request, user)
        # Clear session data
        try:
            del request.session['registration_data']
        except KeyError:
            pass

        messages.success(request, f"Welcome, {user.username}! Your account has been created successfully.")
        user_profile = getattr(user, 'profile', None)
        if user_profile:
            if user_profile.user_type == 'student':
                return redirect('core:student_dashboard')
            elif user_profile.user_type == 'admin':
                return redirect('core:admin_dashboard')
            elif user_profile.user_type == 'osas':
                return redirect('core:osas_dashboard')
        return redirect('core:dashboard_router')

    # If final form invalid, render the final step with errors
    return render(request, 'auth/register_step1.html', {'form': form, 'step': 'final_error'})


def register(request):
    """Session-backed multi-step registration.

    Steps:
      1. Account (username, email, password, user_type)
      2. Personal (first_name, last_name, department, phone)
      3. Student (student_id, campus, year_level) - conditional when user_type == 'student'
    """
    # Determine current step from POST (hidden field) or GET param
    try:
        step = int(request.POST.get('step') or request.GET.get('step') or 1)
    except ValueError:
        step = 1

    # Ensure session storage exists
    registration_data = request.session.get('registration_data', {})

    # Step 1: account
    if step == 1:
        if request.method == 'POST':
            form = RegistrationStep1Form(request.POST)
            if form.is_valid():
                registration_data.update(form.cleaned_data)
                request.session['registration_data'] = registration_data
                # If user_type is student we need step 2+3, otherwise step 2 then finalize
                return redirect(f"{request.path}?step=2")
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = RegistrationStep1Form(initial=registration_data)

        return render(request, 'auth/register_step1.html', {'form': form, 'step': 1})

    # Step 2: personal details
    if step == 2:
        if request.method == 'POST':
            form = RegistrationStep2Form(request.POST)
            if form.is_valid():
                registration_data.update(form.cleaned_data)
                request.session['registration_data'] = registration_data
                # If student, go to step 3, else finalize
                if registration_data.get('user_type') == 'student':
                    return redirect(f"{request.path}?step=3")
                return _finalize_registration(request, registration_data)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = RegistrationStep2Form(initial=registration_data)

        return render(request, 'auth/register_step2.html', {'form': form, 'step': 2})

    # Step 3: student-specific
    if step == 3:
        if request.method == 'POST':
            form = RegistrationStudentStep3Form(request.POST)
            if form.is_valid():
                registration_data.update(form.cleaned_data)
                request.session['registration_data'] = registration_data
                return _finalize_registration(request, registration_data)
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = RegistrationStudentStep3Form(initial=registration_data)

        return render(request, 'auth/register_step3.html', {'form': form, 'step': 3})

    # Fallback: redirect to step 1
    return redirect(f"{request.path}?step=1")


def custom_logout(request):
    """Custom logout view that redirects to landing page."""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('core:landing_page')


def dashboard_router(request):
    """Route users to appropriate dashboard based on their role."""
    if not request.user.is_authenticated:
        return redirect('core:landing_page')
    
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        messages.error(request, 'User profile not found. Please contact administrator.')
        return redirect('core:landing_page')
    
    if user_profile.user_type == 'student':
        return redirect('core:student_dashboard')
    elif user_profile.user_type == 'admin':
        return redirect('core:admin_dashboard')
    elif user_profile.user_type == 'osas':
        return redirect('core:osas_dashboard')
    else:
        messages.error(request, 'Invalid user type. Please contact administrator.')
        return redirect('core:landing_page')


@login_required
def profile_update(request):
    """Update user profile information."""
    user_form = UserUpdateForm(instance=request.user)
    profile_form = UserProfileForm(instance=request.user.profile)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('core:profile_update')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'auth/profile_update.html', context)


# Placeholder dashboard views
@login_required
def student_dashboard(request):
    """Student dashboard with scholarship browser, application tracker, and analytics."""
    if not request.user.profile.is_student:
        messages.error(request, 'Access denied. Student access required.')
        return redirect('core:landing_page')
    
    # Get student's applications
    user_applications = Application.objects.filter(student=request.user).select_related('scholarship')
    
    # Get available scholarships (active and not past deadline)
    available_scholarships = Scholarship.objects.filter(
        is_active=True,
        application_deadline__gt=timezone.now()
    ).exclude(
        id__in=user_applications.values_list('scholarship_id', flat=True)
    ).order_by('application_deadline')
    
    # Get recent notifications
    recent_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    # Dashboard analytics
    analytics = {
        'total_applications': user_applications.count(),
        'pending_applications': user_applications.filter(status='pending').count(),
        'approved_applications': user_applications.filter(status='approved').count(),
        'available_scholarships': available_scholarships.count(),
        'unread_notifications': recent_notifications.count(),
    }
    
    context = {
        'user_applications': user_applications[:5],  # Show recent 5
        'available_scholarships': available_scholarships[:6],  # Show top 6
        'recent_notifications': recent_notifications,
        'analytics': analytics,
    }
    
    return render(request, 'student/dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Administrator dashboard with scholarship management and application overview."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    # Get scholarships created by this admin
    admin_scholarships = Scholarship.objects.filter(
        created_by=request.user
    ).annotate(
        total_applications=Count('applications')
    ).order_by('-created_at')
    
    # Get recent applications across all scholarships
    recent_applications = Application.objects.select_related(
        'student', 'scholarship', 'reviewed_by'
    ).order_by('-submitted_at')[:10]
    
    # Dashboard analytics
    analytics = {
        'total_scholarships': admin_scholarships.count(),
        'active_scholarships': admin_scholarships.filter(is_active=True).count(),
        'total_applications': Application.objects.count(),
        'pending_applications': Application.objects.filter(status='pending').count(),
        'approved_applications': Application.objects.filter(status='approved').count(),
        'scholarships_closing_soon': admin_scholarships.filter(
            is_active=True,
            application_deadline__lt=timezone.now() + timedelta(days=7),
            application_deadline__gt=timezone.now()
        ).count(),
    }
    
    context = {
        'admin_scholarships': admin_scholarships[:5],  # Show recent 5
        'recent_applications': recent_applications,
        'analytics': analytics,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def osas_dashboard(request):
    """OSAS staff dashboard with review queue and decision management."""
    if not request.user.profile.is_osas:
        messages.error(request, 'Access denied. OSAS staff access required.')
        return redirect('core:landing_page')
    
    # Get applications pending review
    pending_applications = Application.objects.filter(
        status='pending'
    ).select_related('student', 'scholarship').order_by('submitted_at')
    
    # Get applications under review by this OSAS staff
    my_reviews = Application.objects.filter(
        reviewed_by=request.user,
        status='under_review'
    ).select_related('student', 'scholarship').order_by('reviewed_at')
    
    # Get recently completed reviews
    recent_reviews = Application.objects.filter(
        reviewed_by=request.user,
        status__in=['approved', 'rejected']
    ).select_related('student', 'scholarship').order_by('-reviewed_at')[:10]
    
    # Dashboard analytics
    analytics = {
        'pending_applications': pending_applications.count(),
        'my_under_review': my_reviews.count(),
        'total_reviews_completed': Application.objects.filter(
            reviewed_by=request.user,
            status__in=['approved', 'rejected']
        ).count(),
        'approved_today': Application.objects.filter(
            reviewed_by=request.user,
            status='approved',
            reviewed_at__date=timezone.now().date()
        ).count(),
        'rejected_today': Application.objects.filter(
            reviewed_by=request.user,
            status='rejected',
            reviewed_at__date=timezone.now().date()
        ).count(),
        'total_pending_system': Application.objects.filter(status='pending').count(),
    }
    
    context = {
        'pending_applications': pending_applications[:8],  # Show top 8
        'my_reviews': my_reviews[:5],  # Show top 5
        'recent_reviews': recent_reviews,
        'analytics': analytics,
    }
    
    return render(request, 'osas/dashboard.html', context)


@login_required
def review_queue(request):
    """OSAS/Admin view to manage application review queue."""
    if not (request.user.profile.is_osas or request.user.profile.is_admin):
        messages.error(request, 'Access denied. OSAS or Administrator access required.')
        return redirect('core:landing_page')
    
    # Get applications for review
    applications = Application.objects.select_related(
        'student', 'scholarship', 'reviewed_by'
    ).order_by('submitted_at')
    
    # Filter by status
    status_filter = request.GET.get('status', 'pending')
    if status_filter and status_filter != 'all':
        applications = applications.filter(status=status_filter)
    
    # Filter by scholarship
    scholarship_filter = request.GET.get('scholarship')
    if scholarship_filter:
        applications = applications.filter(scholarship_id=scholarship_filter)
    
    # Filter by reviewer
    reviewer_filter = request.GET.get('reviewer')
    if reviewer_filter == 'me':
        applications = applications.filter(reviewed_by=request.user)
    elif reviewer_filter == 'unassigned':
        applications = applications.filter(reviewed_by__isnull=True)
    
    # Pagination
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Status counts
    status_counts = {
        'all': Application.objects.count(),
        'pending': Application.objects.filter(status='pending').count(),
        'under_review': Application.objects.filter(status='under_review').count(),
        'approved': Application.objects.filter(status='approved').count(),
        'rejected': Application.objects.filter(status='rejected').count(),
    }
    
    # Get scholarships and reviewers for filters
    scholarships_for_filter = Scholarship.objects.filter(
        applications__isnull=False
    ).distinct().order_by('title')
    
    reviewers_for_filter = User.objects.filter(
        profile__user_type='osas',
        reviewed_applications__isnull=False
    ).distinct().order_by('first_name', 'last_name')
    
    context = {
        'applications': page_obj,  # Changed from page_obj to applications
        'page_obj': page_obj,
        'status_filter': status_filter,
        'scholarship_filter': scholarship_filter,
        'reviewer_filter': reviewer_filter,
        'status_counts': status_counts,
        'scholarships': scholarships_for_filter,  # Changed from scholarships_for_filter
        'reviewers_for_filter': reviewers_for_filter,
    }
    
    return render(request, 'osas/review_queue.html', context)


@login_required
def application_review(request, application_id):
    """OSAS view to review individual application."""
    if not request.user.profile.is_osas:
        messages.error(request, 'Access denied. OSAS staff access required.')
        return redirect('core:landing_page')
    
    application = get_object_or_404(
        Application.objects.select_related('student', 'scholarship', 'reviewed_by'),
        id=application_id
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')
        
        if action in ['approve', 'reject', 'request_info']:
            if action == 'approve':
                # OSAS recommends for approval - Admin will make final decision
                application.mark_as_reviewed(
                    reviewer=request.user,
                    status='osas_approved',
                    comments=comments
                )
                messages.success(request, f'Application recommended for approval. Awaiting admin final decision.')
                
                # Create notification for admins
                from django.contrib.auth.models import User
                admins = User.objects.filter(profile__user_type='admin')
                for admin in admins:
                    Notification.objects.create(
                        recipient=admin,
                        title='New Application Recommended for Approval',
                        message=f'OSAS staff {request.user.get_full_name()} recommends approval for {application.student.get_full_name()}\'s application to {application.scholarship.title}.',
                        notification_type='info',
                        related_application=application
                    )
                    
            elif action == 'reject':
                # OSAS recommends for rejection - Admin will make final decision
                application.mark_as_reviewed(
                    reviewer=request.user,
                    status='osas_rejected',
                    comments=comments
                )
                messages.success(request, f'Application recommended for rejection. Awaiting admin final decision.')
                
                # Create notification for admins
                from django.contrib.auth.models import User
                admins = User.objects.filter(profile__user_type='admin')
                for admin in admins:
                    Notification.objects.create(
                        recipient=admin,
                        title='New Application Recommended for Rejection',
                        message=f'OSAS staff {request.user.get_full_name()} recommends rejection for {application.student.get_full_name()}\'s application to {application.scholarship.title}.',
                        notification_type='warning',
                        related_application=application
                    )
                
            elif action == 'request_info':
                application.mark_as_reviewed(
                    reviewer=request.user,
                    status='additional_info_required',
                    comments=comments
                )
                messages.success(request, f'Additional information requested from {application.student.get_full_name()}.')
                
                # Create notification for student
                Notification.objects.create(
                    recipient=application.student,
                    title='Additional Information Required',
                    message=f'Please provide additional information for your {application.scholarship.title} application.',
                    notification_type='warning',
                    related_application=application
                )
                
            return redirect('core:review_queue')
        
        elif action == 'assign_to_me':
            application.reviewed_by = request.user
            application.status = 'under_review'
            application.reviewed_at = timezone.now()
            application.save()
            messages.success(request, 'Application assigned to you for review.')
    
    # Get student's other applications for context
    student_other_apps = Application.objects.filter(
        student=application.student
    ).exclude(id=application.id).select_related('scholarship')
    
    context = {
        'application': application,
        'student_other_apps': student_other_apps,
    }
    
    return render(request, 'osas/application_review.html', context)


@login_required
def htmx_notifications(request):
    """HTMX endpoint for real-time notifications."""
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'htmx/notifications.html', context)


@login_required
def scholarships_list(request):
    """List all available scholarships for students."""
    if not request.user.profile.is_student:
        messages.error(request, 'Access denied. Student access required.')
        return redirect('core:landing_page')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    
    # Base queryset - active scholarships with future deadlines
    scholarships = Scholarship.objects.filter(
        is_active=True,
        application_deadline__gt=timezone.now()
    )
    
    # Apply search filter
    if search_query:
        scholarships = scholarships.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(eligibility_criteria__icontains=search_query)
        )
    
    # Apply department filter
    if department_filter:
        scholarships = scholarships.filter(
            eligibility_criteria__icontains=department_filter
        )
    
    # Get user's existing applications to exclude applied scholarships
    user_applications = Application.objects.filter(
        student=request.user
    ).values_list('scholarship_id', flat=True)
    
    scholarships = scholarships.exclude(id__in=user_applications)
    scholarships = scholarships.order_by('application_deadline')
    
    # Pagination
    paginator = Paginator(scholarships, 9)  # 9 scholarships per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique departments for filter
    departments = Scholarship.objects.values_list('eligibility_criteria', flat=True).distinct()
    department_keywords = set()
    for criteria in departments:
        if criteria:
            words = criteria.lower().split()
            department_keywords.update([word for word in words if len(word) > 3])
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'department_filter': department_filter,
        'department_keywords': sorted(list(department_keywords))[:10],  # Top 10 keywords
        'user_applications': user_applications,
    }
    
    return render(request, 'student/scholarships_list.html', context)


@login_required
def scholarship_detail(request, scholarship_id):
    """Show detailed view of a scholarship."""
    if not request.user.profile.is_student:
        messages.error(request, 'Access denied. Student access required.')
        return redirect('core:landing_page')
    
    scholarship = get_object_or_404(
        Scholarship.objects.prefetch_related('requirements'),
        id=scholarship_id,
        is_active=True
    )
    
    # Group requirements by category
    requirements_by_category = {}
    for req in scholarship.requirements.all():
        category = req.get_category_display()
        if category not in requirements_by_category:
            requirements_by_category[category] = []
        requirements_by_category[category].append(req)
    
    # Check if user has already applied
    existing_application = Application.objects.filter(
        student=request.user,
        scholarship=scholarship
    ).first()
    
    # Check if application period is still open
    can_apply = (
        not existing_application and 
        scholarship.application_deadline > timezone.now() and
        scholarship.available_slots_remaining > 0
    )
    
    context = {
        'scholarship': scholarship,
        'requirements_by_category': requirements_by_category,
        'existing_application': existing_application,
        'can_apply': can_apply,
    }
    
    return render(request, 'scholarships/detail.html', context)


@login_required
def my_applications(request):
    """Show student's applications with status tracking."""
    if not request.user.profile.is_student:
        messages.error(request, 'Access denied. Student access required.')
        return redirect('core:landing_page')
    
    # Get all user applications
    applications = Application.objects.filter(
        student=request.user
    ).select_related('scholarship', 'reviewed_by').order_by('-submitted_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        applications = applications.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status counts for filter tabs
    status_counts = {
        'all': Application.objects.filter(student=request.user).count(),
        'pending': Application.objects.filter(student=request.user, status='pending').count(),
        'under_review': Application.objects.filter(student=request.user, status='under_review').count(),
        'approved': Application.objects.filter(student=request.user, status='approved').count(),
        'rejected': Application.objects.filter(student=request.user, status='rejected').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter or 'all',
        'status_counts': status_counts,
    }
    
    return render(request, 'student/my_applications.html', context)


@login_required
def manage_scholarships(request):
    """Admin view to manage scholarships."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    # Get scholarships created by this admin
    scholarships = Scholarship.objects.filter(
        created_by=request.user
    ).annotate(
        total_applications=Count('applications'),
        pending_applications=Count('applications', filter=Q(applications__status='pending')),
        approved_applications=Count('applications', filter=Q(applications__status='approved'))
    ).order_by('-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        scholarships = scholarships.filter(is_active=True)
    elif status_filter == 'inactive':
        scholarships = scholarships.filter(is_active=False)
    elif status_filter == 'closing_soon':
        scholarships = scholarships.filter(
            is_active=True,
            application_deadline__lt=timezone.now() + timedelta(days=7),
            application_deadline__gt=timezone.now()
        )
    
    # Pagination
    paginator = Paginator(scholarships, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Status counts for filter tabs
    status_counts = {
        'all': Scholarship.objects.filter(created_by=request.user).count(),
        'active': Scholarship.objects.filter(created_by=request.user, is_active=True).count(),
        'inactive': Scholarship.objects.filter(created_by=request.user, is_active=False).count(),
        'closing_soon': Scholarship.objects.filter(
            created_by=request.user,
            is_active=True,
            application_deadline__lt=timezone.now() + timedelta(days=7),
            application_deadline__gt=timezone.now()
        ).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter or 'all',
        'status_counts': status_counts,
    }
    
    return render(request, 'admin/manage_scholarships.html', context)


@login_required
def view_applications(request):
    """Admin/OSAS view to see all applications across scholarships."""
    if not (request.user.profile.is_admin or request.user.profile.is_osas):
        messages.error(request, 'Access denied. Administrator or OSAS access required.')
        return redirect('core:landing_page')
    
    # Get applications based on user role
    if request.user.profile.is_admin:
        # Admin sees applications for their scholarships
        applications = Application.objects.filter(
            scholarship__created_by=request.user
        ).select_related('student', 'scholarship', 'reviewed_by').order_by('-submitted_at')
    else:
        # OSAS sees all applications
        applications = Application.objects.all().select_related(
            'student', 'scholarship', 'reviewed_by'
        ).order_by('-submitted_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        applications = applications.filter(status=status_filter)
    
    # Filter by scholarship if requested
    scholarship_filter = request.GET.get('scholarship')
    if scholarship_filter:
        applications = applications.filter(scholarship_id=scholarship_filter)
    
    # Pagination
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Status counts for filter tabs
    if request.user.profile.is_admin:
        base_qs = Application.objects.filter(scholarship__created_by=request.user)
        scholarships_for_filter = Scholarship.objects.filter(
            created_by=request.user
        ).order_by('title')
    else:
        base_qs = Application.objects.all()
        scholarships_for_filter = Scholarship.objects.all().order_by('title')
    
    status_counts = {
        'all': base_qs.count(),
        'pending': base_qs.filter(status='pending').count(),
        'under_review': base_qs.filter(status='under_review').count(),
        'approved': base_qs.filter(status='approved').count(),
        'rejected': base_qs.filter(status='rejected').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter or 'all',
        'scholarship_filter': scholarship_filter,
        'status_counts': status_counts,
        'scholarships_for_filter': scholarships_for_filter,
    }
    
    return render(request, 'admin/view_applications.html', context)


@login_required
def assign_application(request, application_id):
    """Assign application to current OSAS/Admin staff member."""
    if not (request.user.profile.is_osas or request.user.profile.is_admin):
        messages.error(request, 'Access denied. OSAS or Administrator access required.')
        return redirect('core:landing_page')
    
    if request.method == 'POST':
        application = get_object_or_404(Application, id=application_id)
        
        # Assign to current user and change status
        application.reviewed_by = request.user
        application.status = 'under_review'
        application.save()
        
        messages.success(request, f'Application for {application.scholarship.title} assigned to you for review.')
        return redirect('core:review_queue')
    
    return redirect('core:review_queue')


@login_required
def review_application(request, application_id):
    """OSAS/Admin view to review individual application."""
    if not (request.user.profile.is_osas or request.user.profile.is_admin):
        messages.error(request, 'Access denied. OSAS or Administrator access required.')
        return redirect('core:landing_page')
    
    application = get_object_or_404(
        Application.objects.select_related('student', 'scholarship', 'reviewed_by'),
        id=application_id
    )
    
    context = {
        'application': application,
    }
    
    return render(request, 'osas/application_review.html', context)


@login_required
def submit_review(request, application_id):
    """Submit review decision for an application - DEPRECATED, redirects to application_review."""
    # This view is deprecated in favor of the two-tier approval system
    # Redirect to the application_review view which handles the new workflow
    return redirect('core:review_application', application_id=application_id)


@login_required
def htmx_mark_notification_read(request, notification_id):
    """HTMX endpoint to mark notification as read."""
    if request.method == 'POST':
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        return HttpResponse('')  # Return empty response to remove the notification
    return HttpResponse('')


@login_required
def htmx_application_status(request, application_id):
    """HTMX endpoint for real-time application status updates."""
    application = get_object_or_404(
        Application.objects.select_related('scholarship', 'reviewed_by'),
        id=application_id,
        student=request.user
    )
    
    context = {
        'application': application,
    }
    
    return render(request, 'htmx/application_status.html', context)


@login_required
def htmx_scholarship_search(request):
    """HTMX endpoint for live scholarship search."""
    if not request.user.profile.is_student:
        return HttpResponse('')
    
    search_query = request.GET.get('q', '').strip()
    
    if len(search_query) < 2:
        return HttpResponse('<div class="px-4 py-2 text-sm text-gray-500">Type at least 2 characters to search...</div>')
    
    # Search scholarships
    scholarships = Scholarship.objects.filter(
        is_active=True,
        application_deadline__gt=timezone.now()
    ).filter(
        Q(title__icontains=search_query) |
        Q(description__icontains=search_query) |
        Q(eligibility_criteria__icontains=search_query)
    )[:5]  # Limit to 5 results for dropdown
    
    # Get user's existing applications to exclude applied scholarships
    user_applications = Application.objects.filter(
        student=request.user
    ).values_list('scholarship_id', flat=True)
    
    scholarships = scholarships.exclude(id__in=user_applications)
    
    context = {
        'scholarships': scholarships,
        'search_query': search_query,
    }
    
    return render(request, 'htmx/scholarship_search.html', context)


@login_required
def htmx_dashboard_stats(request):
    """HTMX endpoint for real-time dashboard statistics."""
    user_profile = request.user.profile
    
    if user_profile.is_student:
        # Student statistics
        stats = {
            'total_applications': Application.objects.filter(student=request.user).count(),
            'pending_applications': Application.objects.filter(student=request.user, status='pending').count(),
            'approved_applications': Application.objects.filter(student=request.user, status='approved').count(),
            'available_scholarships': Scholarship.objects.filter(
                is_active=True,
                application_deadline__gt=timezone.now()
            ).exclude(
                id__in=Application.objects.filter(student=request.user).values_list('scholarship_id', flat=True)
            ).count(),
        }
        template = 'htmx/student_stats.html'
    
    elif user_profile.is_admin:
        # Admin statistics
        stats = {
            'total_scholarships': Scholarship.objects.filter(created_by=request.user).count(),
            'active_scholarships': Scholarship.objects.filter(created_by=request.user, is_active=True).count(),
            'total_applications': Application.objects.filter(scholarship__created_by=request.user).count(),
            'pending_reviews': Application.objects.filter(
                scholarship__created_by=request.user,
                status='pending'
            ).count(),
        }
        template = 'htmx/admin_stats.html'
    
    elif user_profile.is_osas:
        # OSAS statistics
        stats = {
            'pending_applications': Application.objects.filter(status='pending').count(),
            'under_review': Application.objects.filter(status='under_review').count(),
            'my_assigned': Application.objects.filter(reviewer=request.user, status='under_review').count(),
            'approved_today': Application.objects.filter(
                status='approved',
                reviewed_at__date=timezone.now().date()
            ).count(),
        }
        template = 'htmx/osas_stats.html'
    
    else:
        return HttpResponse('')
    
    context = {
        'stats': stats,
    }
    
    return render(request, template, context)


@login_required
def upload_document(request, application_id):
    """Upload documents for an application."""
    application = get_object_or_404(
        Application,
        id=application_id,
        student=request.user
    )
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document_file = form.cleaned_data['document_file']
            document_name = form.cleaned_data['document_name']
            
            # Create document record
            document = ApplicationDocument.objects.create(
                application=application,
                name=document_name,
                file=document_file,
                file_size=document_file.size,
                content_type=document_file.content_type
            )
            
            messages.success(request, f'Document "{document_name}" uploaded successfully.')
            return redirect('core:application_detail', application_id=application.id)
    else:
        form = DocumentUploadForm()
    
    context = {
        'form': form,
        'application': application,
    }
    
    return render(request, 'applications/upload_document.html', context)


@login_required
def delete_document(request, document_id):
    """Delete an uploaded document."""
    document = get_object_or_404(
        ApplicationDocument,
        id=document_id,
        application__student=request.user
    )
    
    if request.method == 'POST':
        application_id = document.application.id
        document_name = document.name
        document.delete()
        
        messages.success(request, f'Document "{document_name}" deleted successfully.')
        return redirect('core:application_detail', application_id=application_id)
    
    context = {
        'document': document,
    }
    
    return render(request, 'applications/confirm_delete_document.html', context)


@login_required
def application_detail(request, application_id):
    """View application details with document management."""
    application = get_object_or_404(
        Application.objects.select_related('scholarship', 'reviewed_by'),
        id=application_id,
        student=request.user
    )
    
    # Get application documents
    documents = application.documents.all().order_by('-uploaded_at')
    
    context = {
        'application': application,
        'documents': documents,
    }
    
    return render(request, 'applications/detail.html', context)


@login_required
def apply_scholarship(request, scholarship_id):
    """Apply for a scholarship with dynamic document requirements."""
    if not request.user.profile.is_student:
        messages.error(request, 'Access denied. Student access required.')
        return redirect('core:landing_page')
    
    scholarship = get_object_or_404(
        Scholarship,
        id=scholarship_id,
        is_active=True
    )
    
    # Check if user already applied
    existing_application = Application.objects.filter(
        student=request.user,
        scholarship=scholarship
    ).first()
    
    if existing_application:
        messages.info(request, 'You have already applied for this scholarship.')
        return redirect('core:my_applications')
    
    # Check if application deadline has passed
    if scholarship.application_deadline <= timezone.now():
        messages.error(request, 'Application deadline for this scholarship has passed.')
        return redirect('core:scholarship_detail', scholarship_id=scholarship.id)
    
    # Check if scholarship has available slots
    if scholarship.available_slots_remaining <= 0:
        messages.error(request, 'No more slots available for this scholarship.')
        return redirect('core:scholarship_detail', scholarship_id=scholarship.id)
    
    if request.method == 'POST':
        from .forms import DynamicApplicationForm
        
        form = DynamicApplicationForm(scholarship=scholarship, data=request.POST, files=request.FILES)
        
        if form.is_valid():
            try:
                # Create the application
                application = form.save(commit=False)
                application.student = request.user
                application.scholarship = scholarship
                application.save()
                
                # Handle document uploads
                for requirement in scholarship.document_requirements.all():
                    field_name = f'document_{requirement.id}'
                    uploaded_file = form.cleaned_data.get(field_name)
                    
                    if uploaded_file:
                        # Create ApplicationDocument
                        ApplicationDocument.objects.create(
                            application=application,
                            document_requirement=requirement,
                            name=f"{requirement.display_name} - {uploaded_file.name}",
                            file=uploaded_file,
                            file_size=uploaded_file.size,
                            content_type=uploaded_file.content_type
                        )
                
                # Create notification for student
                Notification.objects.create(
                    recipient=request.user,
                    title='Application Submitted Successfully',
                    message=f'Your application for {scholarship.title} has been submitted and is now under review.',
                    notification_type='success',
                    related_application=application
                )
                
                messages.success(request, f'Your application for {scholarship.title} has been submitted successfully!')
                return redirect('core:my_applications')
                
            except Exception as e:
                messages.error(request, f'Error submitting application: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from .forms import DynamicApplicationForm
        form = DynamicApplicationForm(scholarship=scholarship)
    
    context = {
        'scholarship': scholarship,
        'form': form,
        'deadline_days': (scholarship.application_deadline - timezone.now()).days,
    }
    
    return render(request, 'students/apply_scholarship.html', context)


@login_required
def bulk_upload_documents(request, application_id):
    """Upload multiple documents for an application using HTMX."""
    application = get_object_or_404(
        Application,
        id=application_id,
        student=request.user
    )
    
    if request.method == 'POST' and request.FILES:
        uploaded_files = request.FILES.getlist('files')
        uploaded_documents = []
        
        for uploaded_file in uploaded_files:
            try:
                # Validate file
                from .forms import FileUploadValidator
                FileUploadValidator.validate_file(uploaded_file)
                
                # Create document
                document = ApplicationDocument.objects.create(
                    application=application,
                    name=uploaded_file.name,
                    file=uploaded_file,
                    file_size=uploaded_file.size,
                    content_type=uploaded_file.content_type
                )
                uploaded_documents.append(document)
                
            except ValidationError as e:
                messages.error(request, f'Error uploading {uploaded_file.name}: {str(e)}')
        
        if uploaded_documents:
            messages.success(request, f'Successfully uploaded {len(uploaded_documents)} document(s).')
        
        # Return HTMX response with updated document list
        if request.headers.get('HX-Request'):
            context = {
                'documents': application.documents.all().order_by('-uploaded_at'),
                'application': application,
            }
            return render(request, 'htmx/document_list.html', context)
    
    return redirect('core:application_detail', application_id=application.id)


@login_required
def create_scholarship(request):
    """Admin view to create a new scholarship."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    if request.method == 'POST':
        form = ScholarshipForm(request.POST)
        if form.is_valid():
            scholarship = form.save(commit=False)
            scholarship.created_by = request.user
            scholarship.save()
            # Save the many-to-many relationships (includes newly created requirements)
            form.save_m2m()
            
            # Handle scholarship requirements
            scholarship_requirements = []
            for key, value in request.POST.items():
                if key.startswith('scholarship_requirement_') and value.strip():
                    scholarship_requirements.append(value.strip())
            
            # Create ScholarshipRequirement objects
            from .models import ScholarshipRequirement
            for idx, req_description in enumerate(scholarship_requirements, start=1):
                ScholarshipRequirement.objects.create(
                    scholarship=scholarship,
                    category='eligibility',  # Default category
                    description=req_description,
                    order=idx
                )
            
            messages.success(request, f'Scholarship "{scholarship.title}" created successfully!')
            return redirect('core:manage_scholarships')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ScholarshipForm()
    
    context = {
        'form': form,
        'title': 'Create Scholarship',
    }
    
    return render(request, 'admin/create_scholarship.html', context)


@login_required
def edit_scholarship(request, scholarship_id):
    """Admin view to edit an existing scholarship."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    scholarship = get_object_or_404(Scholarship, id=scholarship_id, created_by=request.user)
    
    if request.method == 'POST':
        form = ScholarshipForm(request.POST, instance=scholarship)
        if form.is_valid():
            scholarship = form.save()
            
            # Handle scholarship requirements
            # First, delete existing requirements
            from .models import ScholarshipRequirement
            scholarship.requirements.all().delete()
            
            # Then create new ones from the form
            scholarship_requirements = []
            for key, value in request.POST.items():
                if key.startswith('scholarship_requirement_') and value.strip():
                    scholarship_requirements.append(value.strip())
            
            # Create ScholarshipRequirement objects
            for idx, req_description in enumerate(scholarship_requirements, start=1):
                ScholarshipRequirement.objects.create(
                    scholarship=scholarship,
                    category='eligibility',  # Default category
                    description=req_description,
                    order=idx
                )
            
            messages.success(request, f'Scholarship "{scholarship.title}" updated successfully!')
            return redirect('core:manage_scholarships')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ScholarshipForm(instance=scholarship)
    
    context = {
        'form': form,
        'scholarship': scholarship,
        'title': f'Edit Scholarship: {scholarship.title}',
    }
    
    return render(request, 'admin/edit_scholarship.html', context)


@login_required
def manage_document_requirements(request):
    """Admin view to manage document requirements."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    from .models import DocumentRequirement
    from .forms import DocumentRequirementForm
    
    requirements = DocumentRequirement.objects.all().order_by('name')
    
    if request.method == 'POST':
        form = DocumentRequirementForm(request.POST)
        if form.is_valid():
            requirement = form.save()
            messages.success(request, f'Document requirement "{requirement.display_name}" created successfully!')
            return redirect('core:manage_document_requirements')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DocumentRequirementForm()
    
    context = {
        'requirements': requirements,
        'form': form,
    }
    
    return render(request, 'admin/manage_document_requirements.html', context)


@login_required
def toggle_scholarship_status(request, scholarship_id):
    """Admin view to toggle scholarship active status."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    scholarship = get_object_or_404(Scholarship, id=scholarship_id, created_by=request.user)
    
    if request.method == 'POST':
        scholarship.is_active = not scholarship.is_active
        scholarship.save()
        status = "activated" if scholarship.is_active else "deactivated"
        messages.success(request, f'Scholarship "{scholarship.title}" has been {status}.')
    
    return redirect('core:manage_scholarships')


@login_required
def admin_review_application(request, application_id):
    """Admin view to review an application."""
    if not request.user.profile.is_admin:
        messages.error(request, 'Access denied. Administrator access required.')
        return redirect('core:landing_page')
    
    application = get_object_or_404(
        Application.objects.select_related('student', 'scholarship', 'reviewed_by'),
        id=application_id,
        scholarship__created_by=request.user
    )
    
    if request.method == 'POST':
        decision = request.POST.get('decision')
        comments = request.POST.get('comments', '')
        
        if decision in ['approved', 'rejected', 'additional_info_required']:
            # Update application status
            application.status = decision
            application.reviewed_by = request.user
            application.reviewer_comments = comments
            application.reviewed_at = timezone.now()
            application.save()
            
            # Create notification for student
            if decision == 'approved':
                notification_title = 'Scholarship Application Approved!'
                notification_message = f'Congratulations! Your application for {application.scholarship.title} has been approved.'
                notification_type = 'success'
            elif decision == 'rejected':
                notification_title = 'Scholarship Application Update'
                notification_message = f'Your application for {application.scholarship.title} has been reviewed.'
                notification_type = 'info'
            else:  # additional_info_required
                notification_title = 'Additional Information Required'
                notification_message = f'Please provide additional information for your {application.scholarship.title} application.'
                notification_type = 'warning'
            
            Notification.objects.create(
                recipient=application.student,
                title=notification_title,
                message=notification_message,
                notification_type=notification_type,
                related_application=application
            )
            
            messages.success(request, f'Application reviewed successfully.')
            return redirect('core:view_applications')
        else:
            messages.error(request, 'Invalid decision.')
    
    context = {
        'application': application,
    }
    
    return render(request, 'admin/review_application.html', context)


@login_required
def ajax_create_document_requirement(request):
    """AJAX endpoint to create a new document requirement."""
    if not request.user.profile.is_admin:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    if request.method == 'POST':
        try:
            doc_type = request.POST.get('doc_type')
            custom_name = request.POST.get('custom_name', '')
            description = request.POST.get('description', '')
            formats = request.POST.get('formats', 'PDF, DOC, DOCX, JPG, PNG')
            max_size = request.POST.get('max_size', '5')
            is_required = request.POST.get('is_required') == 'true'
            
            # Validate required fields
            if not doc_type:
                return JsonResponse({'success': False, 'error': 'Document type is required'}, status=400)
            
            if doc_type == 'other' and not custom_name:
                return JsonResponse({'success': False, 'error': 'Custom name is required for "Other" document type'}, status=400)
            
            # Create the document requirement
            doc_req = DocumentRequirement.objects.create(
                name=doc_type,
                custom_name=custom_name if doc_type == 'other' else '',
                description=description,
                is_required=is_required,
                file_format_requirements=formats,
                max_file_size_mb=int(max_size) if max_size.isdigit() else 5
            )
            
            # Return the created requirement data
            return JsonResponse({
                'success': True,
                'requirement': {
                    'id': doc_req.id,
                    'name': doc_req.name,
                    'display_name': doc_req.display_name,
                    'description': doc_req.description,
                    'is_required': doc_req.is_required,
                    'file_format_requirements': doc_req.file_format_requirements,
                    'max_file_size_mb': doc_req.max_file_size_mb
                }
            })
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

