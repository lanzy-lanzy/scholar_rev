"""
Script to create test data for OSAS review queue testing.
Run with: python manage.py shell < create_test_data.py
"""

from django.contrib.auth.models import User
from core.models import UserProfile, Scholarship, Application
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

print("=" * 60)
print("Creating Test Data for OSAS Review Queue")
print("=" * 60)

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
    print(f"✓ Created admin user: {admin_user.username}")
else:
    print(f"✓ Admin user exists: {admin_user.username}")

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
for i in range(1, 4):
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
        print(f"✓ Created student: {student.username}")
    else:
        print(f"✓ Student exists: {student.username}")
    
    # Ensure student profile
    profile, created = UserProfile.objects.get_or_create(
        user=student,
        defaults={
            'user_type': 'student',
            'student_id': f'2024-000{i}',
            'year_level': '1st'
        }
    )
    if profile.user_type != 'student':
        profile.user_type = 'student'
        profile.student_id = f'2024-000{i}'
        profile.year_level = '1st'
        profile.save()
    
    students.append(student)

# 3. Create scholarships
scholarships = []
scholarship_data = [
    {
        'title': 'Academic Excellence Scholarship',
        'description': 'For students with outstanding academic performance',
        'eligibility_criteria': 'GPA of 3.5 or higher',
        'award_amount': Decimal('50000.00'),
        'available_slots': 5
    },
    {
        'title': 'Financial Assistance Grant',
        'description': 'For students with financial need',
        'eligibility_criteria': 'Family income below poverty line',
        'award_amount': Decimal('30000.00'),
        'available_slots': 10
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
        print(f"✓ Created scholarship: {scholarship.title}")
    else:
        print(f"✓ Scholarship exists: {scholarship.title}")
    scholarships.append(scholarship)

# 4. Create applications
print("\nCreating applications...")
for i, student in enumerate(students):
    for j, scholarship in enumerate(scholarships):
        # Create different statuses for testing
        if i == 0 and j == 0:
            status = 'pending'
        elif i == 1 and j == 0:
            status = 'pending'
        elif i == 2 and j == 0:
            status = 'pending'
        elif i == 0 and j == 1:
            status = 'pending'
        else:
            status = 'pending'
        
        application, created = Application.objects.get_or_create(
            student=student,
            scholarship=scholarship,
            defaults={
                'personal_statement': f'I am {student.first_name} {student.last_name} applying for {scholarship.title}. I believe I deserve this scholarship because of my dedication to academic excellence and community service.',
                'gpa': Decimal('3.75'),
                'status': status,
                'additional_info': 'I am committed to maintaining high academic standards.'
            }
        )
        if created:
            print(f"  ✓ Created application: {student.username} → {scholarship.title} ({status})")
        else:
            print(f"  ✓ Application exists: {student.username} → {scholarship.title}")

# 5. Summary
print("\n" + "=" * 60)
print("Test Data Summary:")
print("=" * 60)
print(f"Users: {User.objects.count()}")
print(f"  - Admins: {UserProfile.objects.filter(user_type='admin').count()}")
print(f"  - OSAS: {UserProfile.objects.filter(user_type='osas').count()}")
print(f"  - Students: {UserProfile.objects.filter(user_type='student').count()}")
print(f"Scholarships: {Scholarship.objects.count()}")
print(f"Applications: {Application.objects.count()}")
print(f"  - Pending: {Application.objects.filter(status='pending').count()}")
print(f"  - Under Review: {Application.objects.filter(status='under_review').count()}")
print(f"  - Approved: {Application.objects.filter(status='approved').count()}")
print(f"  - Rejected: {Application.objects.filter(status='rejected').count()}")

print("\n" + "=" * 60)
print("Test Credentials:")
print("=" * 60)
print("OSAS Staff:")
print("  Username: osas_staff")
print("  Password: osas123")
print("\nAdmin:")
print("  Username: admin")
print("  Password: admin123")
print("\nStudents:")
print("  Username: student1, student2, student3")
print("  Password: student123")
print("\n" + "=" * 60)
print("✓ Test data created successfully!")
print("=" * 60)
