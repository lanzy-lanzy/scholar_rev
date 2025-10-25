"""
Forms for the Scholarship Management System.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import os
from typing import List

from .models import UserProfile, Scholarship, Application, Notification, DocumentRequirement


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form with additional fields."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Enter your email address'
        })
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Enter your last name'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=UserProfile.USER_TYPE_CHOICES,
        initial='student',
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'
        })
    )
    
    # Student-specific fields
    student_id = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Enter your student ID'
        })
    )
    
    campus = forms.ChoiceField(
        choices=[('', 'Select Campus')] + UserProfile.CAMPUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'
        })
    )
    
    year_level = forms.ChoiceField(
        choices=UserProfile.YEAR_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'
        })
    )
    
    # Optional fields
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Enter your department'
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Enter your phone number'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Confirm your password'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        student_id = cleaned_data.get('student_id')
        campus = cleaned_data.get('campus')
        year_level = cleaned_data.get('year_level')
        
        # Validate student-specific fields
        if user_type == 'student':
            if not student_id:
                raise ValidationError("Student ID is required for students.")
            if not campus:
                raise ValidationError("Campus is required for students.")
            if not year_level:
                raise ValidationError("Year level is required for students.")
            
            # Check for duplicate student ID
            if UserProfile.objects.filter(student_id=student_id).exists():
                raise ValidationError("A student with this ID already exists.")
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create user profile with additional fields
            profile = UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                student_id=self.cleaned_data.get('student_id'),
                campus=self.cleaned_data.get('campus'),
                year_level=self.cleaned_data.get('year_level'),
                department=self.cleaned_data.get('department'),
                phone_number=self.cleaned_data.get('phone_number')
            )
        
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information."""
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone_number', 'student_id', 'campus', 'department', 'year_level']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
                'accept': 'image/*'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter your phone number'
            }),
            'student_id': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter your student ID'
            }),
            'campus': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            }),
            'department': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter your department'
            }),
            'year_level': forms.Select(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white'
            }),
        }


class UserUpdateForm(forms.ModelForm):
    """Form for updating basic user information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter your email address'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email exists for another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email


class DocumentRequirementForm(forms.ModelForm):
    """Form for creating document requirements."""
    
    class Meta:
        model = DocumentRequirement
        fields = [
            'name', 'custom_name', 'description', 'is_required', 
            'file_format_requirements', 'max_file_size_mb'
        ]
        widgets = {
            'name': forms.Select(attrs={
                'class': 'form-input w-full border rounded-lg transition-all duration-200'
            }),
            'custom_name': forms.TextInput(attrs={
                'class': 'form-input w-full border rounded-lg transition-all duration-200',
                'placeholder': 'Enter custom document name (for "Other" type)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input w-full border rounded-lg transition-all duration-200',
                'rows': 3,
                'placeholder': 'Additional instructions or description for this document'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
            }),
            'file_format_requirements': forms.TextInput(attrs={
                'class': 'form-input w-full border rounded-lg transition-all duration-200',
                'placeholder': 'e.g., PDF, DOC, DOCX, JPG, PNG'
            }),
            'max_file_size_mb': forms.NumberInput(attrs={
                'class': 'form-input w-full border rounded-lg transition-all duration-200',
                'min': '1',
                'max': '50',
                'placeholder': 'Maximum file size in MB'
            }),
        }


class ScholarshipForm(forms.ModelForm):
    """Form for creating and updating scholarships."""
    
    # Dynamic document requirements
    document_requirements = forms.ModelMultipleChoiceField(
        queryset=DocumentRequirement.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'document-requirement-checkbox'
        }),
        required=False,
        help_text="Select which documents are required for this scholarship application"
    )
    
    class Meta:
        model = Scholarship
        fields = [
            'title', 'description', 'award_amount', 'available_slots',
            'application_deadline', 'eligibility_criteria', 'document_requirements', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter scholarship title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'rows': 4,
                'placeholder': 'Describe the scholarship'
            }),
            'award_amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter amount in PHP',
                'step': '0.01'
            }),
            'available_slots': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Number of available slots',
                'min': '1'
            }),
            'application_deadline': forms.DateTimeInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'type': 'datetime-local',
                'placeholder': 'Select date and time'
            }),
            'eligibility_criteria': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'rows': 3,
                'placeholder': 'Describe eligibility criteria'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded dark:bg-gray-700 dark:border-gray-600'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing scholarship, set the initial document requirements
        if self.instance.pk:
            self.fields['document_requirements'].initial = self.instance.document_requirements.all()


class FileUploadValidator:
    """Validator for uploaded files."""
    
    # Allowed file types and their MIME types
    ALLOWED_TYPES = {
        'pdf': ['application/pdf'],
        'doc': ['application/msword'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'jpg': ['image/jpeg'],
        'jpeg': ['image/jpeg'],
        'png': ['image/png'],
        'txt': ['text/plain'],
    }
    
    # Maximum file size in bytes (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    def validate_file(cls, uploaded_file: UploadedFile) -> None:
        """Validate uploaded file."""
        # Check file size
        if uploaded_file.size > cls.MAX_FILE_SIZE:
            raise ValidationError(f"File size must be less than {cls.MAX_FILE_SIZE // (1024*1024)}MB.")
        
        # Get file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
        
        # Check if extension is allowed
        if file_extension not in cls.ALLOWED_TYPES:
            allowed_extensions = ', '.join(cls.ALLOWED_TYPES.keys())
            raise ValidationError(f"File type '{file_extension}' is not allowed. Allowed types: {allowed_extensions}")
        
        # Validate MIME type using python-magic (if available)
        try:
            import magic
            file_content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            
            mime_type = magic.from_buffer(file_content, mime=True)
            
            allowed_mimes = cls.ALLOWED_TYPES[file_extension]
            if mime_type not in allowed_mimes:
                raise ValidationError(f"File content does not match expected type for '{file_extension}' files.")
                
        except ImportError:
            # python-magic not available, skip MIME type validation
            pass
        except Exception as e:
            # Other errors in file validation
            raise ValidationError(f"Error validating file: {str(e)}")


class DocumentUploadForm(forms.Form):
    """Form for uploading application documents."""
    
    document_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Enter document name (e.g., Transcript, ID Copy)'
        })
    )
    
    document_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'mt-1 block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt'
        })
    )
    
    def clean_document_file(self):
        """Validate uploaded document file."""
        document_file = self.cleaned_data.get('document_file')
        
        if document_file:
            FileUploadValidator.validate_file(document_file)
        
        return document_file


class ApplicationForm(forms.ModelForm):
    """Form for scholarship applications."""
    
    class Meta:
        model = Application
        fields = [
            'personal_statement', 'gpa', 'supporting_documents', 'additional_info'
        ]
        widgets = {
            'personal_statement': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'rows': 6,
                'placeholder': 'Write your personal statement explaining why you deserve this scholarship...'
            }),
            'gpa': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'placeholder': 'Enter your GPA (e.g., 3.5)',
                'step': '0.01',
                'min': '0.0',
                'max': '4.0'
            }),
            'supporting_documents': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 cursor-pointer dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'rows': 4,
                'placeholder': 'Any additional information you would like to provide...'
            }),
        }


class DynamicApplicationForm(forms.ModelForm):
    """Dynamic form for scholarship applications with document requirements."""
    
    class Meta:
        model = Application
        fields = ['personal_statement', 'gpa', 'additional_info']
        widgets = {
            'personal_statement': forms.Textarea(attrs={
                'class': 'form-input w-full border rounded-lg transition-all duration-200',
                'rows': 6,
                'placeholder': 'Write your personal statement explaining why you deserve this scholarship...'
            }),
            'gpa': forms.NumberInput(attrs={
                'class': 'form-input w-full border rounded-lg transition-all duration-200',
                'placeholder': 'Enter your GPA (e.g., 3.5)',
                'step': '0.01',
                'min': '0.0',
                'max': '4.0'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-input w-full border rounded-lg transition-all duration-200',
                'rows': 4,
                'placeholder': 'Any additional information you would like to provide...'
            }),
        }
    
    def __init__(self, scholarship=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scholarship = scholarship
        
        if scholarship:
            # Add dynamic file fields for each document requirement
            for requirement in scholarship.document_requirements.all():
                field_name = f'document_{requirement.id}'
                self.fields[field_name] = forms.FileField(
                    label=requirement.display_name,
                    required=requirement.is_required,
                    help_text=f"{requirement.description or ''} (Max size: {requirement.max_file_size_mb}MB, Formats: {requirement.file_format_requirements})",
                    widget=forms.FileInput(attrs={
                        'class': 'form-input w-full border rounded-lg transition-all duration-200',
                        'accept': self._get_accept_string(requirement.file_format_requirements),
                        'data-max-size': requirement.max_file_size_mb * 1024 * 1024,  # Convert to bytes
                    })
                )
    
    def _get_accept_string(self, file_formats):
        """Convert file format requirements to HTML accept attribute."""
        format_mapping = {
            'PDF': '.pdf',
            'DOC': '.doc',
            'DOCX': '.docx',
            'JPG': '.jpg,.jpeg',
            'JPEG': '.jpg,.jpeg',
            'PNG': '.png',
            'TXT': '.txt'
        }
        
        formats = [fmt.strip().upper() for fmt in file_formats.split(',')]
        accept_list = []
        
        for fmt in formats:
            if fmt in format_mapping:
                accept_list.append(format_mapping[fmt])
        
        return ','.join(accept_list)
    
    def clean(self):
        cleaned_data = super().clean()
        
        if self.scholarship:
            # Validate each document requirement
            for requirement in self.scholarship.document_requirements.all():
                field_name = f'document_{requirement.id}'
                file_field = cleaned_data.get(field_name)
                
                # Check if field exists in form
                if field_name not in self.fields:
                    continue
                
                if requirement.is_required and not file_field:
                    error_msg = f'{requirement.display_name} is required.'
                    self.add_error(field_name, error_msg)
                
                if file_field:
                    # Validate file size
                    max_size = requirement.max_file_size_mb * 1024 * 1024
                    if file_field.size > max_size:
                        self.add_error(
                            field_name, 
                            f'File size must be less than {requirement.max_file_size_mb}MB.'
                        )
                    
                    # Validate file extension
                    allowed_formats = [fmt.strip().lower() for fmt in requirement.file_format_requirements.split(',')]
                    file_extension = file_field.name.split('.')[-1].lower()
                    
                    if file_extension not in allowed_formats:
                        self.add_error(
                            field_name,
                            f'File format "{file_extension}" is not allowed. Allowed formats: {requirement.file_format_requirements}'
                        )
        
        return cleaned_data


class ScholarshipFilterForm(forms.Form):
    """Form for filtering scholarships."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Search scholarships...'
        })
    )
    
    min_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Min amount'
        })
    )
    
    max_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white',
            'placeholder': 'Max amount'
        })
    )