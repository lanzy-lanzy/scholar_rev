from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_admin_approval

app_name = 'core'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='landing_page'),
    
    # Authentication URLs
    path('auth/register/', views.register, name='register'),
    path('auth/login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('auth/logout/', views.custom_logout, name='logout'),
    path('auth/profile/', views.profile_update, name='profile_update'),
    
    # Dashboard routing
    path('dashboard/', views.dashboard_router, name='dashboard_router'),
    
    # Role-specific dashboards
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('osas/', views.osas_dashboard, name='osas_dashboard'),
    
    # Admin-specific URLs for scholarships
    path('dashboard/admin/scholarships/create/', views.create_scholarship, name='create_scholarship'),
    path('dashboard/admin/scholarships/<int:scholarship_id>/edit/', views.edit_scholarship, name='edit_scholarship'),
    path('dashboard/admin/scholarships/<int:scholarship_id>/toggle/', views.toggle_scholarship_status, name='toggle_scholarship_status'),
    
    # Admin-specific URLs for applications
    path('dashboard/admin/applications/<int:application_id>/review/', views.admin_review_application, name='admin_review_application'),
    
    # Admin final approval URLs (two-tier approval system)
    path('dashboard/admin/pending-approvals/', views_admin_approval.admin_pending_approvals, name='admin_pending_approvals'),
    path('dashboard/admin/final-decision/<int:application_id>/', views_admin_approval.admin_final_decision, name='admin_final_decision'),
    path('dashboard/admin/review-history/', views_admin_approval.admin_review_history, name='admin_review_history'),
    
    # Student-specific URLs
    path('scholarships/', views.scholarships_list, name='scholarships_list'),
    path('scholarships/<int:scholarship_id>/', views.scholarship_detail, name='scholarship_detail'),
    path('scholarships/<int:scholarship_id>/apply/', views.apply_scholarship, name='apply_scholarship'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('applications/<int:application_id>/upload/', views.upload_document, name='upload_document'),
    path('applications/<int:application_id>/bulk-upload/', views.bulk_upload_documents, name='bulk_upload_documents'),
    path('documents/<int:document_id>/delete/', views.delete_document, name='delete_document'),
    
    # Admin-specific URLs
    path('manage-scholarships/', views.manage_scholarships, name='manage_scholarships'),
    path('view-applications/', views.view_applications, name='view_applications'),
    path('manage-document-requirements/', views.manage_document_requirements, name='manage_document_requirements'),
    
    path('review-queue/', views.review_queue, name='review_queue'),
    path('review/<int:application_id>/', views.review_application, name='review_application'),
    path('assign/<int:application_id>/', views.assign_application, name='assign_application'),
    path('submit-review/<int:application_id>/', views.submit_review, name='submit_review'),
    
    # HTMX endpoints
    path('htmx/notifications/', views.htmx_notifications, name='htmx_notifications'),
    path('htmx/mark-notification-read/<int:notification_id>/', views.htmx_mark_notification_read, name='htmx_mark_notification_read'),
    path('htmx/application-status/<int:application_id>/', views.htmx_application_status, name='htmx_application_status'),
    path('htmx/scholarship-search/', views.htmx_scholarship_search, name='htmx_scholarship_search'),
    path('htmx/dashboard-stats/', views.htmx_dashboard_stats, name='htmx_dashboard_stats'),
    
    # AJAX endpoints
    path('ajax/create-document-requirement/', views.ajax_create_document_requirement, name='ajax_create_document_requirement'),
]