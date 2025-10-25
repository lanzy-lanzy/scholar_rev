from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from django.utils import timezone
from decimal import Decimal
import os


def user_document_path(instance, filename):
    """Generate file path for user documents."""
    return f'applications/{instance.student.username}/{filename}'


class UserProfile(models.Model):
    """Extended user profile with role-based information."""
    
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Administrator'),
        ('osas', 'OSAS Staff'),
    ]
    
    YEAR_LEVEL_CHOICES = [
        ('1st', '1st Year'),
        ('2nd', '2nd Year'),
        ('3rd', '3rd Year'),
        ('4th', '4th Year'),
        ('graduate', 'Graduate Student'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    year_level = models.CharField(max_length=10, choices=YEAR_LEVEL_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, help_text='Upload a profile picture (JPG, PNG, GIF - Max 5MB)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_user_type_display()})"
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_osas(self):
        return self.user_type == 'osas'


class DocumentRequirement(models.Model):
    """Document requirements for scholarships."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('certificate_enrollment', 'Certificate of Enrollment'),
        ('certificate_grades', 'Certificate of Grades'),
        ('certificate_indigency', 'Certificate of Indigency'),
        ('birth_certificate', 'Birth Certificate'),
        ('barangay_clearance', 'Barangay Clearance'),
        ('police_clearance', 'Police Clearance'),
        ('medical_certificate', 'Medical Certificate'),
        ('recommendation_letter', 'Letter of Recommendation'),
        ('essay', 'Essay/Personal Statement'),
        ('transcript', 'Official Transcript'),
        ('tax_return', 'Tax Return/ITR'),
        ('payslip', 'Payslip/Income Certificate'),
        ('other', 'Other Document'),
    ]
    
    name = models.CharField(max_length=100, choices=DOCUMENT_TYPE_CHOICES)
    custom_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Custom name for 'Other' document type"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional description or instructions for this document"
    )
    is_required = models.BooleanField(default=True)
    file_format_requirements = models.CharField(
        max_length=100,
        default="PDF, DOC, DOCX, JPG, PNG",
        help_text="Accepted file formats"
    )
    max_file_size_mb = models.PositiveIntegerField(
        default=5,
        help_text="Maximum file size in MB"
    )
    
    class Meta:
        verbose_name = 'Document Requirement'
        verbose_name_plural = 'Document Requirements'
    
    def __str__(self):
        if self.name == 'other' and self.custom_name:
            return self.custom_name
        return self.get_name_display()
    
    @property
    def display_name(self):
        """Get the display name for the document requirement."""
        if self.name == 'other' and self.custom_name:
            return self.custom_name
        return self.get_name_display()


class Scholarship(models.Model):
    """Scholarship offerings managed by administrators."""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    eligibility_criteria = models.TextField()
    award_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    application_deadline = models.DateTimeField()
    available_slots = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    document_requirements = models.ManyToManyField(
        DocumentRequirement,
        blank=True,
        related_name='scholarships',
        help_text="Select required documents for this scholarship"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='scholarships_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Scholarship'
        verbose_name_plural = 'Scholarships'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_application_open(self):
        """Check if applications are still being accepted."""
        return self.is_active and self.application_deadline > timezone.now()
    
    @property
    def days_until_deadline(self):
        """Calculate days remaining until deadline."""
        if self.application_deadline > timezone.now():
            delta = self.application_deadline - timezone.now()
            return delta.days
        return 0
    
    @property
    def applications_count(self):
        """Count total applications for this scholarship."""
        return self.applications.count()
    
    @property
    def approved_applications_count(self):
        """Count approved applications."""
        return self.applications.filter(status='approved').count()
    
    @property
    def available_slots_remaining(self):
        """Calculate remaining slots."""
        return max(0, self.available_slots - self.approved_applications_count)


class ScholarshipRequirement(models.Model):
    """Detailed requirements for scholarships."""
    
    REQUIREMENT_CATEGORY_CHOICES = [
        ('academic', 'Academic Requirements'),
        ('documentation', 'Documentation Requirements'),
        ('eligibility', 'Eligibility Requirements'),
        ('additional', 'Additional Requirements'),
    ]
    
    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name='requirements'
    )
    category = models.CharField(
        max_length=20,
        choices=REQUIREMENT_CATEGORY_CHOICES,
        default='eligibility'
    )
    description = models.TextField(
        help_text="Requirement description"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or clarifications"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order within category"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'order', 'created_at']
        verbose_name = 'Scholarship Requirement'
        verbose_name_plural = 'Scholarship Requirements'
    
    def __str__(self):
        return f"{self.scholarship.title} - {self.get_category_display()}: {self.description[:50]}"


class Application(models.Model):
    """Student applications for scholarships."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('osas_approved', 'OSAS Recommended for Approval'),
        ('osas_rejected', 'OSAS Recommended for Rejection'),
        ('approved', 'Approved by Admin'),
        ('rejected', 'Rejected by Admin'),
        ('additional_info_required', 'Additional Information Required'),
    ]
    
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    scholarship = models.ForeignKey(
        Scholarship, 
        on_delete=models.CASCADE, 
        related_name='applications'
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    personal_statement = models.TextField()
    gpa = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('4.00'))
        ]
    )
    supporting_documents = models.FileField(
        upload_to=user_document_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])
        ],
        help_text='Upload supporting documents (PDF, Word, or Image files)',
        blank=True,
        null=True
    )
    additional_info = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviewed_applications',
        null=True, 
        blank=True
    )
    reviewer_comments = models.TextField(blank=True, null=True)
    
    # Admin final decision fields
    final_decision_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='final_decisions',
        null=True,
        blank=True,
        help_text='Admin who made the final approval/rejection decision'
    )
    final_decision_at = models.DateTimeField(null=True, blank=True)
    final_decision_comments = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        ordering = ['-submitted_at']
        unique_together = ['student', 'scholarship']  # One application per student per scholarship
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.scholarship.title}"
    
    @property
    def status_display_class(self):
        """Return CSS class for status display."""
        status_classes = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'under_review': 'bg-blue-100 text-blue-800',
            'osas_approved': 'bg-teal-100 text-teal-800',
            'osas_rejected': 'bg-purple-100 text-purple-800',
            'approved': 'bg-green-100 text-green-800',
            'rejected': 'bg-red-100 text-red-800',
            'additional_info_required': 'bg-orange-100 text-orange-800',
        }
        return status_classes.get(self.status, 'bg-gray-100 text-gray-800')
    
    def can_be_edited(self):
        """Check if application can still be edited."""
        return self.status in ['pending', 'additional_info_required']
    
    def mark_as_reviewed(self, reviewer, status, comments=None):
        """Mark application as reviewed with decision."""
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.status = status
        if comments:
            self.reviewer_comments = comments
        self.save()


class Notification(models.Model):
    """System notifications for users."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    related_application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
    
    @property
    def type_display_class(self):
        """Return CSS class for notification type display."""
        type_classes = {
            'info': 'bg-blue-100 text-blue-800 border-blue-200',
            'warning': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'success': 'bg-green-100 text-green-800 border-green-200',
            'error': 'bg-red-100 text-red-800 border-red-200',
        }
        return type_classes.get(self.notification_type, 'bg-gray-100 text-gray-800 border-gray-200')
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save()


class ApplicationDocument(models.Model):
    """Model for storing application documents."""
    
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    document_requirement = models.ForeignKey(
        DocumentRequirement,
        on_delete=models.CASCADE,
        related_name='uploaded_documents',
        help_text="The document requirement this file fulfills",
        null=True,
        blank=True
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Name or description of the document"
    )
    
    file = models.FileField(
        upload_to='application_documents/%Y/%m/%d/',
        help_text="Uploaded document file",
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])
        ]
    )
    
    file_size = models.PositiveIntegerField(
        help_text="File size in bytes"
    )
    
    content_type = models.CharField(
        max_length=100,
        help_text="MIME type of the file"
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Application Document"
        verbose_name_plural = "Application Documents"
    
    def __str__(self):
        return f"{self.name} - {self.application.student.username}"

    @property
    def file_size_human(self):
        """Return human-readable file size."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    def delete(self, *args, **kwargs):
        """Delete the file when the model instance is deleted."""
        if self.file and hasattr(self.file, 'delete'):
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
