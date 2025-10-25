"""
Script to populate existing students with campus assignments for testing.
This distributes students evenly across the three campuses.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from core.models import UserProfile

def populate_campuses():
    """Assign campuses to existing students for testing."""
    
    # Get all student profiles without campus assignment
    students = UserProfile.objects.filter(
        user_type='student',
        campus__isnull=True
    ).select_related('user')
    
    if not students.exists():
        print("No students found without campus assignment.")
        print("\nChecking all students...")
        all_students = UserProfile.objects.filter(user_type='student').select_related('user')
        
        if not all_students.exists():
            print("✗ No student accounts found in the system.")
            return
        
        print(f"\n✓ Found {all_students.count()} students. All already have campus assignments:")
        for student in all_students:
            campus_display = student.get_campus_display() if student.campus else "Not assigned"
            print(f"  - {student.user.get_full_name()} ({student.student_id}): {campus_display}")
        return
    
    print(f"Found {students.count()} students without campus assignment.")
    print("\nDistributing students across campuses...\n")
    
    # Campus options
    campuses = ['dumingag', 'mati', 'canuto']
    campus_names = {
        'dumingag': 'Dumingag Campus',
        'mati': 'Mati Campus',
        'canuto': 'Canuto Campus'
    }
    
    # Distribute students evenly across campuses
    updated_count = 0
    campus_counts = {'dumingag': 0, 'mati': 0, 'canuto': 0}
    
    for index, student in enumerate(students):
        # Assign campus in round-robin fashion
        campus = campuses[index % len(campuses)]
        
        student.campus = campus
        student.save()
        
        campus_counts[campus] += 1
        updated_count += 1
        
        student_id_display = student.student_id if student.student_id else "N/A"
        print(f"✓ {student.user.get_full_name():30} (ID: {student_id_display:15}) → {campus_names[campus]}")
    
    print("\n" + "="*80)
    print("Campus Assignment Summary:")
    print("="*80)
    print(f"Total students updated: {updated_count}")
    print(f"\nDistribution:")
    print(f"  • Dumingag Campus: {campus_counts['dumingag']} students")
    print(f"  • Mati Campus:     {campus_counts['mati']} students")
    print(f"  • Canuto Campus:   {campus_counts['canuto']} students")
    print("="*80)
    
    print("\n✓ Campus population completed successfully!")
    print("\nYou can now:")
    print("  1. Test student registration with campus selection")
    print("  2. Filter applications by campus in admin panel")
    print("  3. View campus information in application details")


def show_current_distribution():
    """Show current campus distribution of all students."""
    
    all_students = UserProfile.objects.filter(user_type='student').select_related('user')
    
    if not all_students.exists():
        print("No student accounts found in the system.")
        return
    
    print("\n" + "="*80)
    print("Current Student Campus Distribution:")
    print("="*80)
    
    campus_groups = {
        'dumingag': [],
        'mati': [],
        'canuto': [],
        'unassigned': []
    }
    
    for student in all_students:
        if student.campus:
            campus_groups[student.campus].append(student)
        else:
            campus_groups['unassigned'].append(student)
    
    campus_names = {
        'dumingag': 'Dumingag Campus',
        'mati': 'Mati Campus',
        'canuto': 'Canuto Campus',
        'unassigned': 'Unassigned'
    }
    
    for campus_key, students_list in campus_groups.items():
        if students_list or campus_key == 'unassigned':
            print(f"\n{campus_names[campus_key]}: {len(students_list)} students")
            for student in students_list:
                student_id_display = student.student_id if student.student_id else "N/A"
                print(f"  - {student.user.get_full_name()} (ID: {student_id_display})")
    
    print("\n" + "="*80)
    print(f"Total Students: {all_students.count()}")
    print("="*80)


if __name__ == '__main__':
    print("="*80)
    print("Student Campus Population Script")
    print("="*80)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--show':
        show_current_distribution()
    else:
        try:
            populate_campuses()
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
