from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import UserProfile, Scholarship, Application, Notification, DocumentRequirement
from .forms import CustomUserCreationForm


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_profile_creation(self):
        """Test that UserProfile is created automatically."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user_type, 'student')
    
    def test_user_profile_str(self):
        """Test string representation of UserProfile."""
        expected = f"{self.user.get_full_name()} (Student)"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_user_type_properties(self):
        """Test user type properties."""
        profile = self.user.profile
        
        # Test student type
        profile.user_type = 'student'
        profile.save()
        self.assertTrue(profile.is_student)
        self.assertFalse(profile.is_admin)
        self.assertFalse(profile.is_osas)
        
        # Test admin type
        profile.user_type = 'admin'
        profile.save()
        self.assertFalse(profile.is_student)
        self.assertTrue(profile.is_admin)
        self.assertFalse(profile.is_osas)
        
        # Test OSAS type
        profile.user_type = 'osas'
        profile.save()
        self.assertFalse(profile.is_student)
        self.assertFalse(profile.is_admin)
        self.assertTrue(profile.is_osas)


class ScholarshipModelTest(TestCase):
    """Test cases for Scholarship model."""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com'
        )
        self.admin_user.profile.user_type = 'admin'
        self.admin_user.profile.save()
        
        self.scholarship = Scholarship.objects.create(
            title='Test Scholarship',
            description='Test description',
            eligibility_criteria='Test criteria',
            award_amount=Decimal('1000.00'),
            application_deadline=timezone.now() + timedelta(days=30),
            available_slots=5,
            created_by=self.admin_user
        )
    
    def test_scholarship_str(self):
        """Test string representation of Scholarship."""
        self.assertEqual(str(self.scholarship), 'Test Scholarship')
    
    def test_is_application_open(self):
        """Test application open status."""
        # Test open application
        self.assertTrue(self.scholarship.is_application_open)
        
        # Test closed application (past deadline)
        self.scholarship.application_deadline = timezone.now() - timedelta(days=1)
        self.scholarship.save()
        self.assertFalse(self.scholarship.is_application_open)
        
        # Test inactive scholarship
        self.scholarship.is_active = False
        self.scholarship.application_deadline = timezone.now() + timedelta(days=30)
        self.scholarship.save()
        self.assertFalse(self.scholarship.is_application_open)
    
    def test_days_until_deadline(self):
        """Test days until deadline calculation."""
        # Test future deadline
        future_deadline = timezone.now() + timedelta(days=10)
        self.scholarship.application_deadline = future_deadline
        self.scholarship.save()
        self.assertGreaterEqual(self.scholarship.days_until_deadline, 9)
        
        # Test past deadline
        past_deadline = timezone.now() - timedelta(days=5)
        self.scholarship.application_deadline = past_deadline
        self.scholarship.save()
        self.assertEqual(self.scholarship.days_until_deadline, 0)
    
    def test_applications_count(self):
        """Test applications count."""
        self.assertEqual(self.scholarship.applications_count, 0)
        
        # Create a student and application
        student = User.objects.create_user(username='student', email='student@example.com')
        Application.objects.create(
            student=student,
            scholarship=self.scholarship,
            personal_statement='Test statement',
            gpa=Decimal('3.5')
        )
        
        self.assertEqual(self.scholarship.applications_count, 1)
    
    def test_available_slots_remaining(self):
        """Test available slots calculation."""
        self.assertEqual(self.scholarship.available_slots_remaining, 5)
        
        # Create approved application
        student = User.objects.create_user(username='student', email='student@example.com')
        application = Application.objects.create(
            student=student,
            scholarship=self.scholarship,
            personal_statement='Test statement',
            gpa=Decimal('3.5'),
            status='approved'
        )
        
        self.assertEqual(self.scholarship.available_slots_remaining, 4)


class ApplicationModelTest(TestCase):
    """Test cases for Application model."""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com')
        self.student_user = User.objects.create_user(username='student', email='student@example.com')
        self.osas_user = User.objects.create_user(username='osas', email='osas@example.com')
        self.osas_user.profile.user_type = 'osas'
        self.osas_user.profile.save()
        
        self.scholarship = Scholarship.objects.create(
            title='Test Scholarship',
            description='Test description',
            eligibility_criteria='Test criteria',
            award_amount=Decimal('1000.00'),
            application_deadline=timezone.now() + timedelta(days=30),
            created_by=self.admin_user
        )
        
        self.application = Application.objects.create(
            student=self.student_user,
            scholarship=self.scholarship,
            personal_statement='Test statement',
            gpa=Decimal('3.5')
        )
    
    def test_application_str(self):
        """Test string representation of Application."""
        expected = f"{self.student_user.get_full_name()} - {self.scholarship.title}"
        self.assertEqual(str(self.application), expected)
    
    def test_can_be_edited(self):
        """Test if application can be edited."""
        # Test pending status
        self.application.status = 'pending'
        self.assertTrue(self.application.can_be_edited())
        
        # Test additional info required status
        self.application.status = 'additional_info_required'
        self.assertTrue(self.application.can_be_edited())
        
        # Test approved status
        self.application.status = 'approved'
        self.assertFalse(self.application.can_be_edited())
        
        # Test rejected status
        self.application.status = 'rejected'
        self.assertFalse(self.application.can_be_edited())
    
    def test_mark_as_reviewed(self):
        """Test marking application as reviewed."""
        self.application.mark_as_reviewed(
            reviewer=self.osas_user,
            status='approved',
            comments='Great application!'
        )
        
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'approved')
        self.assertEqual(self.application.reviewed_by, self.osas_user)
        self.assertEqual(self.application.reviewer_comments, 'Great application!')
        self.assertIsNotNone(self.application.reviewed_at)
    
    def test_status_display_class(self):
        """Test status display CSS classes."""
        test_cases = [
            ('pending', 'bg-yellow-100 text-yellow-800'),
            ('under_review', 'bg-blue-100 text-blue-800'),
            ('approved', 'bg-green-100 text-green-800'),
            ('rejected', 'bg-red-100 text-red-800'),
        ]
        
        for status, expected_class in test_cases:
            self.application.status = status
            self.assertEqual(self.application.status_display_class, expected_class)


class NotificationModelTest(TestCase):
    """Test cases for Notification model."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Test message',
            notification_type='info'
        )
    
    def test_notification_str(self):
        """Test string representation of Notification."""
        expected = f"{self.user.username} - Test Notification"
        self.assertEqual(str(self.notification), expected)
    
    def test_mark_as_read(self):
        """Test marking notification as read."""
        self.assertFalse(self.notification.is_read)
        self.notification.mark_as_read()
        self.assertTrue(self.notification.is_read)
    
    def test_type_display_class(self):
        """Test notification type display CSS classes."""
        test_cases = [
            ('info', 'bg-blue-100 text-blue-800 border-blue-200'),
            ('warning', 'bg-yellow-100 text-yellow-800 border-yellow-200'),
            ('success', 'bg-green-100 text-green-800 border-green-200'),
            ('error', 'bg-red-100 text-red-800 border-red-200'),
        ]
        
        for notification_type, expected_class in test_cases:
            self.notification.notification_type = notification_type
            self.assertEqual(self.notification.type_display_class, expected_class)


class CustomUserCreationFormTest(TestCase):
    """Test cases for CustomUserCreationForm."""
    
    def test_valid_student_form(self):
        """Test valid student registration form."""
        form_data = {
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstudent@example.com',
            'user_type': 'student',
            'student_id': '2024-001',
            'department': 'Computer Science',
            'year_level': '1st',
            'phone_number': '+1234567890',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'newstudent')
        self.assertEqual(user.profile.user_type, 'student')
        self.assertEqual(user.profile.student_id, '2024-001')
    
    def test_student_missing_required_fields(self):
        """Test student form with missing required fields."""
        form_data = {
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstudent@example.com',
            'user_type': 'student',
            # Missing student_id and year_level
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Student ID is required for students.', form.errors['__all__'])
    
    def test_duplicate_student_id(self):
        """Test form with duplicate student ID."""
        # Create existing user with student ID
        existing_user = User.objects.create_user(username='existing', email='existing@example.com')
        existing_user.profile.student_id = '2024-001'
        existing_user.profile.save()
        
        form_data = {
            'username': 'newstudent',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstudent@example.com',
            'user_type': 'student',
            'student_id': '2024-001',  # Duplicate ID
            'year_level': '1st',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('A student with this ID already exists.', form.errors['__all__'])


class ViewsTest(TestCase):
    """Test cases for views."""
    
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123'
        )
        self.student_user.profile.user_type = 'student'
        self.student_user.profile.save()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.admin_user.profile.user_type = 'admin'
        self.admin_user.profile.save()
        
        self.osas_user = User.objects.create_user(
            username='osas',
            email='osas@example.com',
            password='testpass123'
        )
        self.osas_user.profile.user_type = 'osas'
        self.osas_user.profile.save()
    
    def test_landing_page(self):
        """Test landing page view."""
        response = self.client.get(reverse('core:landing_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Scholarship Management System')
    
    def test_register_view_GET(self):
        """Test registration view GET request."""
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')
    
    def test_dashboard_router_student(self):
        """Test dashboard router for student user."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('core:dashboard_router'))
        self.assertRedirects(response, reverse('core:student_dashboard'))
    
    def test_dashboard_router_admin(self):
        """Test dashboard router for admin user."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('core:dashboard_router'))
        self.assertRedirects(response, reverse('core:admin_dashboard'))
    
    def test_dashboard_router_osas(self):
        """Test dashboard router for OSAS user."""
        self.client.login(username='osas', password='testpass123')
        response = self.client.get(reverse('core:dashboard_router'))
        self.assertRedirects(response, reverse('core:osas_dashboard'))
    
    def test_dashboard_router_unauthenticated(self):
        """Test dashboard router for unauthenticated user."""
        response = self.client.get(reverse('core:dashboard_router'))
        self.assertRedirects(response, reverse('core:landing_page'))
    
    def test_profile_update_view(self):
        """Test profile update view."""
        self.client.login(username='student', password='testpass123')
        response = self.client.get(reverse('core:profile_update'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Update Profile Information')
    
    def test_login_required_views(self):
        """Test that login is required for protected views."""
        protected_urls = [
            'core:student_dashboard',
            'core:admin_dashboard',
            'core:osas_dashboard',
            'core:profile_update',
        ]
        
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            # Check that it redirects to login (status 302)
            self.assertEqual(response.status_code, 302)
            # Check that the redirect URL contains login
            self.assertIn('login', response.url)


class DynamicRequirementsTest(TestCase):
    """Test cases for dynamic document requirements feature."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.admin_user.profile.user_type = 'admin'
        self.admin_user.profile.save()
        
        # Create some existing document requirements
        self.existing_req = DocumentRequirement.objects.create(
            name='certificate_enrollment',
            description='Certificate of Enrollment',
            is_required=True,
            file_format_requirements='PDF, DOC, DOCX',
            max_file_size_mb=5
        )
    
    def test_create_scholarship_with_dynamic_requirements(self):
        """Test creating scholarship with dynamic document requirements."""
        self.client.login(username='admin', password='testpass123')
        
        # Prepare form data with dynamic requirements
        form_data = {
            'title': 'Test Scholarship with Dynamic Reqs',
            'description': 'Test description',
            'eligibility_criteria': 'Test criteria',
            'award_amount': '1000.00',
            'application_deadline': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M'),
            'available_slots': 5,
            'is_active': True,
            # Existing requirement
            'document_requirements': [self.existing_req.id],
            # Dynamic requirements
            'new_doc_type_1': 'other',
            'new_doc_custom_name_1': 'Research Proposal',
            'new_doc_description_1': 'Submit your research proposal',
            'new_doc_formats_1': 'PDF, DOC, DOCX',
            'new_doc_max_size_1': '10',
            'new_doc_required_1': 'on',
            # Second dynamic requirement
            'new_doc_type_2': 'recommendation_letter',
            'new_doc_description_2': 'Letter from faculty member',
            'new_doc_formats_2': 'PDF',
            'new_doc_max_size_2': '5',
            'new_doc_required_2': 'on',
        }
        
        response = self.client.post(reverse('core:create_scholarship'), data=form_data)
        
        # Check that scholarship was created
        self.assertEqual(Scholarship.objects.count(), 1)
        scholarship = Scholarship.objects.first()
        
        # Check that dynamic requirements were created
        self.assertGreaterEqual(DocumentRequirement.objects.count(), 3)  # 1 existing + 2 new
        
        # Check that requirements are associated with scholarship
        self.assertGreaterEqual(scholarship.document_requirements.count(), 3)
        
        # Check custom requirement details
        custom_req = DocumentRequirement.objects.filter(name='other', custom_name='Research Proposal').first()
        self.assertIsNotNone(custom_req)
        self.assertEqual(custom_req.description, 'Submit your research proposal')
        self.assertEqual(custom_req.max_file_size_mb, 10)
        self.assertTrue(custom_req.is_required)
    
    def test_create_scholarship_without_dynamic_requirements(self):
        """Test creating scholarship without dynamic requirements."""
        self.client.login(username='admin', password='testpass123')
        
        form_data = {
            'title': 'Test Scholarship',
            'description': 'Test description',
            'eligibility_criteria': 'Test criteria',
            'award_amount': '1000.00',
            'application_deadline': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M'),
            'available_slots': 5,
            'is_active': True,
            'document_requirements': [self.existing_req.id],
        }
        
        response = self.client.post(reverse('core:create_scholarship'), data=form_data)
        
        # Check that scholarship was created
        self.assertEqual(Scholarship.objects.count(), 1)
        scholarship = Scholarship.objects.first()
        
        # Check that only existing requirement is associated
        self.assertEqual(scholarship.document_requirements.count(), 1)
    
    def test_dynamic_requirement_with_custom_name(self):
        """Test that custom name is required for 'other' document type."""
        self.client.login(username='admin', password='testpass123')
        
        form_data = {
            'title': 'Test Scholarship',
            'description': 'Test description',
            'eligibility_criteria': 'Test criteria',
            'award_amount': '1000.00',
            'application_deadline': (timezone.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M'),
            'available_slots': 5,
            'is_active': True,
            'new_doc_type_1': 'other',
            'new_doc_custom_name_1': 'Portfolio',  # Custom name provided
            'new_doc_formats_1': 'PDF, JPG, PNG',
            'new_doc_max_size_1': '10',
        }
        
        response = self.client.post(reverse('core:create_scholarship'), data=form_data)
        
        # Check that requirement was created with custom name
        custom_req = DocumentRequirement.objects.filter(name='other', custom_name='Portfolio').first()
        self.assertIsNotNone(custom_req)
        self.assertEqual(str(custom_req), 'Portfolio')  # Should display custom name
