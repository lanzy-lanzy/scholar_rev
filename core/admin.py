from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Scholarship, Application, Notification, ApplicationDocument


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('user_type', 'student_id', 'department', 'year_level', 'phone_number')


class UserAdmin(BaseUserAdmin):
    """Extended User admin with profile inline."""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__user_type')
    
    def get_user_type(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_user_type_display()
        return 'No Profile'
    get_user_type.short_description = 'User Type'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile."""
    list_display = ('user', 'user_type', 'student_id', 'department', 'year_level')
    list_filter = ('user_type', 'department', 'year_level')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'student_id')
    ordering = ('user__username',)


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    """Admin interface for Scholarship."""
    list_display = ('title', 'award_amount', 'application_deadline', 'available_slots', 'is_active', 'created_by')
    list_filter = ('is_active', 'created_at', 'application_deadline')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'applications_count', 'approved_applications_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'eligibility_criteria')
        }),
        ('Award Details', {
            'fields': ('award_amount', 'available_slots', 'application_deadline')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'applications_count', 'approved_applications_count'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new scholarship
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Application."""
    list_display = ('student', 'scholarship', 'status', 'gpa', 'submitted_at', 'reviewed_by')
    list_filter = ('status', 'submitted_at', 'reviewed_at', 'scholarship')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'scholarship__title')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at', 'reviewed_at')
    
    fieldsets = (
        ('Application Details', {
            'fields': ('student', 'scholarship', 'status')
        }),
        ('Student Information', {
            'fields': ('personal_statement', 'gpa', 'supporting_documents', 'additional_info')
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'reviewed_at', 'reviewer_comments'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'scholarship', 'reviewed_by')


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    """Admin interface for ApplicationDocument."""
    list_display = ('name', 'application', 'file_size_human', 'content_type', 'uploaded_at')
    list_filter = ('content_type', 'uploaded_at')
    search_fields = ('name', 'application__student__username', 'application__scholarship__title')
    ordering = ('-uploaded_at',)
    readonly_fields = ('file_size', 'content_type', 'uploaded_at', 'file_size_human')
    
    fieldsets = (
        ('Document Information', {
            'fields': ('application', 'name', 'file')
        }),
        ('File Details', {
            'fields': ('file_size', 'content_type', 'file_size_human'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('application__student', 'application__scholarship')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification."""
    list_display = ('recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)