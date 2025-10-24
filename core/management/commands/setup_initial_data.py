from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from core.models import UserProfile, Scholarship, Application, Notification


class Command(BaseCommand):
    help = 'Setup initial data for the scholarship management system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up initial data...'))
        
        # Create users
        self.create_users()
        
        # Create scholarships
        self.create_scholarships()
        
        # Create sample applications
        self.create_applications()
        
        # Create notifications
        self.create_notifications()
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed!'))

    def create_users(self):
        """Create sample users with different roles."""
        
        # Admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@scholar.edu',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            admin_user.profile.user_type = 'admin'
            admin_user.profile.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')
        
        # OSAS staff user
        osas_user, created = User.objects.get_or_create(
            username='osas_staff',
            defaults={
                'email': 'osas@scholar.edu',
                'first_name': 'OSAS',
                'last_name': 'Staff',
            }
        )
        if created:
            osas_user.set_password('osas123')
            osas_user.save()
            osas_user.profile.user_type = 'osas'
            osas_user.profile.save()
            self.stdout.write(f'Created OSAS user: {osas_user.username}')
        
        # Sample students
        students_data = [
            {
                'username': 'student1',
                'email': 'john.doe@student.edu',
                'first_name': 'John',
                'last_name': 'Doe',
                'student_id': '2023-001',
                'department': 'Computer Science',
                'year_level': '3rd',
                'phone_number': '+1234567890'
            },
            {
                'username': 'student2',
                'email': 'jane.smith@student.edu',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'student_id': '2023-002',
                'department': 'Mathematics',
                'year_level': '2nd',
                'phone_number': '+1234567891'
            },
            {
                'username': 'student3',
                'email': 'bob.wilson@student.edu',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'student_id': '2023-003',
                'department': 'Engineering',
                'year_level': '4th',
                'phone_number': '+1234567892'
            }
        ]
        
        for student_data in students_data:
            user, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                
                # Update profile
                profile = user.profile
                profile.user_type = 'student'
                profile.student_id = student_data['student_id']
                profile.department = student_data['department']
                profile.year_level = student_data['year_level']
                profile.phone_number = student_data['phone_number']
                profile.save()
                
                self.stdout.write(f'Created student user: {user.username}')

    def create_scholarships(self):
        """Create sample scholarships."""
        
        admin_user = User.objects.get(username='admin')
        
        scholarships_data = [
            {
                'title': 'Academic Excellence Scholarship',
                'description': 'Merit-based scholarship for students with outstanding academic performance.',
                'eligibility_criteria': 'Minimum GPA of 3.5, enrolled in at least 12 credit hours, demonstrated leadership experience.',
                'award_amount': Decimal('5000.00'),
                'application_deadline': timezone.now() + timedelta(days=30),
                'available_slots': 5,
            },
            {
                'title': 'Need-Based Financial Aid',
                'description': 'Financial assistance for students demonstrating economic need.',
                'eligibility_criteria': 'Family income below $50,000, full-time enrollment, maintain minimum 2.5 GPA.',
                'award_amount': Decimal('3000.00'),
                'application_deadline': timezone.now() + timedelta(days=45),
                'available_slots': 10,
            },
            {
                'title': 'STEM Innovation Grant',
                'description': 'Support for students pursuing degrees in Science, Technology, Engineering, and Mathematics.',
                'eligibility_criteria': 'Enrolled in STEM program, minimum 3.0 GPA, research or project proposal required.',
                'award_amount': Decimal('4000.00'),
                'application_deadline': timezone.now() + timedelta(days=60),
                'available_slots': 3,
            },
            {
                'title': 'Community Service Scholarship',
                'description': 'Recognition for students with exceptional community service contributions.',
                'eligibility_criteria': 'Minimum 100 hours community service, letters of recommendation, essay required.',
                'award_amount': Decimal('2500.00'),
                'application_deadline': timezone.now() + timedelta(days=20),
                'available_slots': 8,
            },
            {
                'title': 'Graduate Student Research Fellowship',
                'description': 'Fellowship for graduate students conducting research in their field of study.',
                'eligibility_criteria': 'Graduate student status, research proposal, faculty advisor recommendation.',
                'award_amount': Decimal('7500.00'),
                'application_deadline': timezone.now() + timedelta(days=90),
                'available_slots': 2,
            }
        ]
        
        for scholarship_data in scholarships_data:
            scholarship, created = Scholarship.objects.get_or_create(
                title=scholarship_data['title'],
                defaults={
                    **scholarship_data,
                    'created_by': admin_user,
                }
            )
            if created:
                self.stdout.write(f'Created scholarship: {scholarship.title}')

    def create_applications(self):
        """Create sample applications."""
        
        students = User.objects.filter(profile__user_type='student')
        scholarships = Scholarship.objects.all()
        
        if not students.exists() or not scholarships.exists():
            return
        
        applications_data = [
            {
                'student': students[0],  # John Doe
                'scholarship': scholarships[0],  # Academic Excellence
                'status': 'pending',
                'personal_statement': 'I am passionate about academic excellence and have maintained a 3.8 GPA throughout my studies. I believe this scholarship will help me continue my educational journey and contribute to my field.',
                'gpa': Decimal('3.80'),
                'additional_info': 'President of Computer Science Student Association, Volunteer tutor for underclassmen.'
            },
            {
                'student': students[1],  # Jane Smith
                'scholarship': scholarships[1],  # Need-Based
                'status': 'under_review',
                'personal_statement': 'Coming from a low-income family, this scholarship would significantly help me complete my education without the burden of excessive student loans.',
                'gpa': Decimal('3.20'),
                'additional_info': 'Work part-time to support family, maintain good grades despite financial challenges.'
            },
            {
                'student': students[2],  # Bob Wilson
                'scholarship': scholarships[2],  # STEM Innovation
                'status': 'approved',
                'personal_statement': 'My research in renewable energy systems aligns perfectly with the STEM Innovation Grant goals. I am excited to contribute to sustainable technology development.',
                'gpa': Decimal('3.65'),
                'additional_info': 'Published paper on solar panel efficiency, intern at tech startup.'
            },
            {
                'student': students[0],  # John Doe (second application)
                'scholarship': scholarships[3],  # Community Service
                'status': 'rejected',
                'personal_statement': 'I have dedicated over 150 hours to community service, including organizing food drives and tutoring local students.',
                'gpa': Decimal('3.80'),
                'additional_info': 'Volunteer at local shelter, organized charity events.'
            }
        ]
        
        for app_data in applications_data:
            application, created = Application.objects.get_or_create(
                student=app_data['student'],
                scholarship=app_data['scholarship'],
                defaults=app_data
            )
            if created:
                # Set review information for reviewed applications
                if app_data['status'] in ['approved', 'rejected', 'under_review']:
                    osas_user = User.objects.filter(profile__user_type='osas').first()
                    if osas_user:
                        application.reviewed_by = osas_user
                        application.reviewed_at = timezone.now() - timedelta(days=1)
                        if app_data['status'] == 'approved':
                            application.reviewer_comments = 'Excellent academic record and strong leadership qualities. Approved for scholarship award.'
                        elif app_data['status'] == 'rejected':
                            application.reviewer_comments = 'While the applicant shows good community service, the GPA requirement was not met for this specific scholarship.'
                        else:
                            application.reviewer_comments = 'Application is currently being reviewed. Additional documentation may be requested.'
                        application.save()
                
                self.stdout.write(f'Created application: {application.student.username} -> {application.scholarship.title}')

    def create_notifications(self):
        """Create sample notifications."""
        
        students = User.objects.filter(profile__user_type='student')
        applications = Application.objects.all()
        
        if not students.exists():
            return
        
        notifications_data = [
            {
                'recipient': students[0],
                'title': 'Application Submitted Successfully',
                'message': 'Your application for Academic Excellence Scholarship has been submitted and is being reviewed.',
                'notification_type': 'success',
                'related_application': applications.filter(student=students[0]).first() if applications.exists() else None,
            },
            {
                'recipient': students[1],
                'title': 'Application Under Review',
                'message': 'Your application for Need-Based Financial Aid is currently under review by our committee.',
                'notification_type': 'info',
                'related_application': applications.filter(student=students[1]).first() if applications.exists() else None,
            },
            {
                'recipient': students[2],
                'title': 'Scholarship Approved!',
                'message': 'Congratulations! Your application for STEM Innovation Grant has been approved.',
                'notification_type': 'success',
                'related_application': applications.filter(student=students[2]).first() if applications.exists() else None,
            },
            {
                'recipient': students[0],
                'title': 'New Scholarship Available',
                'message': 'A new scholarship matching your profile has been posted. Check it out!',
                'notification_type': 'info',
            },
            {
                'recipient': students[1],
                'title': 'Application Deadline Reminder',
                'message': 'Reminder: The deadline for Community Service Scholarship is approaching in 5 days.',
                'notification_type': 'warning',
            }
        ]
        
        for notif_data in notifications_data:
            notification, created = Notification.objects.get_or_create(
                recipient=notif_data['recipient'],
                title=notif_data['title'],
                defaults=notif_data
            )
            if created:
                self.stdout.write(f'Created notification: {notification.title} for {notification.recipient.username}')