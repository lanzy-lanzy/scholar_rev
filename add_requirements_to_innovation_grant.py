#!/usr/bin/env python
"""Add requirements to STEM Innovation Grant"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from core.models import Scholarship, ScholarshipRequirement

# Get the STEM Innovation Grant
scholarship = Scholarship.objects.get(id=3, title='STEM Innovation Grant')

print(f"Found scholarship: {scholarship.title} (ID: {scholarship.id})")

# Clear existing requirements
scholarship.requirements.all().delete()

# Add Academic Requirements
ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='academic',
    description='Minimum GPA of 3.0',
    notes='Based on cumulative GPA from all semesters',
    order=0
)

ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='academic',
    description='Enrolled in STEM program (Science, Technology, Engineering, Mathematics)',
    order=1
)

ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='academic',
    description='No failing grades in the current semester',
    order=2
)

# Add Documentation Requirements
ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='documentation',
    description='Official transcript of records',
    notes='Must be sealed and signed by registrar',
    order=0
)

ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='documentation',
    description='Research or project proposal (2-3 pages)',
    notes='Should outline your STEM innovation project',
    order=1
)

ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='documentation',
    description='Letter of recommendation from STEM faculty member',
    order=2
)

# Add Eligibility Requirements
ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='eligibility',
    description='Must be enrolled full-time (minimum 15 units)',
    order=0
)

ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='eligibility',
    description='Philippine citizen or permanent resident',
    order=1
)

# Add Additional Requirements
ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='additional',
    description='Commitment to complete research/project within academic year',
    order=0
)

ScholarshipRequirement.objects.create(
    scholarship=scholarship,
    category='additional',
    description='Willingness to present findings at end-of-year symposium',
    notes='Presentation can be poster or oral format',
    order=1
)

print(f"\n✅ Successfully added {scholarship.requirements.count()} requirements to {scholarship.title}!")
print("\nRequirements by category:")

for category in ['academic', 'documentation', 'eligibility', 'additional']:
    reqs = scholarship.requirements.filter(category=category)
    if reqs.exists():
        print(f"\n{category.upper()}:")
        for req in reqs:
            print(f"  - {req.description}")
            if req.notes:
                print(f"    Note: {req.notes}")

print(f"\n🔗 View at: http://localhost:8000/scholarships/{scholarship.id}/")
