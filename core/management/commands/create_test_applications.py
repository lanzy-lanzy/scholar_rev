"""
Management command to create test applications for OSAS review queue.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile, Scholarship, Application
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create test applications for OSAS review queue testing'

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.WARNING('Creating Test Data for OSAS Review Queue'))
        self.stdout.write('=' * 70)

        # 1. Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@scholar.edu',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Created admin user: {admin_user.username}'))
        else:
            self.stdout.write(f'✓ Admin user exists: {admin_user.username}')

        # Ensure admin profile
        admin_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'user_type': 'admin'}
        )
        if admin_profile.user_type != 'admin':
            admin_profile.user_type = 'admin'
            admin_profile.save()

        # 2. Create or get student users
        students = []
        for i in range(1, 6):  # Create 5 students
            student, created = User.objects.get_or_create(
                username=f'student{i}',
                defaults={
                    'email': f'student{i}@scholar.edu',
                    'first_name': f'Student',
                    'last_name': f'Number {i}',
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created student: {student.username}'))
            else:
                self.stdout.write(f'✓ Student exists: {student.username}')
            
            # Ensure student profile
            profile, created = UserProfile.objects.get_or_create(
                user=student,
                defaults={
                    'user_type': 'student',
                    'student_id': f'2024-000{i}',
                    'year_level': ['1st', '2nd', '3rd', '4th'][i % 4],
                    'department': 'Computer Science'
                }
            )
            if profile.user_type != 'student':
                profile.user_type = 'student'
                profile.student_id = f'2024-000{i}'
                profile.year_level = ['1st', '2nd', '3rd', '4th'][i % 4]
                profile.department = 'Computer Science'
                profile.save()
            
            students.append(student)

        # 3. Create scholarships
        scholarships = []
        scholarship_data = [
            {
                'title': 'Academic Excellence Scholarship',
                'description': 'For students with outstanding academic performance',
                'eligibility_criteria': 'GPA of 3.5 or higher, enrolled full-time',
                'award_amount': Decimal('50000.00'),
                'available_slots': 5
            },
            {
                'title': 'Financial Assistance Grant',
                'description': 'For students with financial need',
                'eligibility_criteria': 'Family income below poverty line, good academic standing',
                'award_amount': Decimal('30000.00'),
                'available_slots': 10
            },
            {
                'title': 'STEM Excellence Award',
                'description': 'For students excelling in Science, Technology, Engineering, and Mathematics',
                'eligibility_criteria': 'STEM major, GPA 3.0 or higher',
                'award_amount': Decimal('40000.00'),
                'available_slots': 3
            },
        ]

        for data in scholarship_data:
            scholarship, created = Scholarship.objects.get_or_create(
                title=data['title'],
                created_by=admin_user,
                defaults={
                    'description': data['description'],
                    'eligibility_criteria': data['eligibility_criteria'],
                    'award_amount': data['award_amount'],
                    'available_slots': data['available_slots'],
                    'application_deadline': timezone.now() + timedelta(days=30),
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created scholarship: {scholarship.title}'))
            else:
                self.stdout.write(f'✓ Scholarship exists: {scholarship.title}')
            scholarships.append(scholarship)

        # 4. Create applications with various statuses
        self.stdout.write('\nCreating applications...')
        
        gpa_values = [Decimal('3.75'), Decimal('3.50'), Decimal('3.90'), Decimal('3.25'), Decimal('3.60')]
        
        for i, student in enumerate(students):
            for j, scholarship in enumerate(scholarships):
                # Skip some combinations to have varied data
                if (i + j) % 3 == 2:
                    continue
                
                application, created = Application.objects.get_or_create(
                    student=student,
                    scholarship=scholarship,
                    defaults={
                        'personal_statement': f'I am {student.first_name} {student.last_name}, a dedicated student applying for the {scholarship.title}. '
                                            f'I believe I deserve this scholarship because of my commitment to academic excellence and community service. '
                                            f'Throughout my academic journey, I have maintained a strong GPA while actively participating in various '
                                            f'extracurricular activities. This scholarship would greatly help me achieve my educational goals.',
                        'gpa': gpa_values[i % len(gpa_values)],
                        'status': 'pending',
                        'additional_info': f'I am currently in my {["1st", "2nd", "3rd", "4th"][i % 4]} year of study in Computer Science. '
                                         f'I am passionate about technology and committed to making a positive impact in my community.'
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ Created: {student.username} → {scholarship.title[:30]}... (pending)'
                    ))

        # 5. Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('Test Data Summary:'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'  - Admins: {UserProfile.objects.filter(user_type="admin").count()}')
        self.stdout.write(f'  - OSAS: {UserProfile.objects.filter(user_type="osas").count()}')
        self.stdout.write(f'  - Students: {UserProfile.objects.filter(user_type="student").count()}')
        self.stdout.write(f'Scholarships: {Scholarship.objects.count()}')
        self.stdout.write(f'Applications: {Application.objects.count()}')
        self.stdout.write(f'  - Pending: {Application.objects.filter(status="pending").count()}')
        self.stdout.write(f'  - Under Review: {Application.objects.filter(status="under_review").count()}')
        self.stdout.write(f'  - Approved: {Application.objects.filter(status="approved").count()}')
        self.stdout.write(f'  - Rejected: {Application.objects.filter(status="rejected").count()}')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('Test Credentials:'))
        self.stdout.write('=' * 70)
        self.stdout.write(self.style.WARNING('OSAS Staff:'))
        self.stdout.write('  Username: osas_staff')
        self.stdout.write('  Password: osas123')
        self.stdout.write(self.style.WARNING('\nAdmin:'))
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: admin123')
        self.stdout.write(self.style.WARNING('\nStudents:'))
        self.stdout.write('  Username: student1, student2, student3, student4, student5')
        self.stdout.write('  Password: student123')
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✓ Test data created successfully!'))
        self.stdout.write(self.style.SUCCESS('✓ Refresh the Review Queue page to see applications'))
        self.stdout.write('=' * 70)
