#!/usr/bin/env python
"""Script to add test requirements to STEM scholarship"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from core.models import Scholarship, ScholarshipRequirement

# Get the STEM scholarship
stem_scholarship = Scholarship.objects.filter(title__icontains='STEM').first()

if stem_scholarship:
    print(f"Found scholarship: {stem_scholarship.title}")
    
    # Clear existing requirements
    stem_scholarship.requirements.all().delete()
    
    # Add Academic Requirements
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='academic',
        description='Minimum GPA of 3.0 in STEM courses',
        notes='Cumulative GPA from all STEM-related courses',
        order=0
    )
    
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='academic',
        description='Completed at least 30 credit hours',
        order=1
    )
    
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='academic',
        description='No failing grades in the current semester',
        notes='All courses must have passing grades',
        order=2
    )
    
    # Add Documentation Requirements
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='documentation',
        description='Official transcript of records',
        notes='Must be sealed and signed by the registrar',
        order=0
    )
    
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='documentation',
        description='Research or project proposal (2-3 pages)',
        notes='Should outline your STEM project or research plan',
        order=1
    )
    
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='documentation',
        description='Letter of recommendation from STEM faculty',
        order=2
    )
    
    # Add Eligibility Requirements
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='eligibility',
        description='Must be enrolled in a STEM program',
        notes='Science, Technology, Engineering, or Mathematics degree program',
        order=0
    )
    
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='eligibility',
        description='Full-time student status (minimum 12 units)',
        order=1
    )
    
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='eligibility',
        description='Philippine citizen or permanent resident',
        order=2
    )
    
    # Add Additional Requirements
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='additional',
        description='Commitment to complete the research/project within the academic year',
        order=0
    )
    
    ScholarshipRequirement.objects.create(
        scholarship=stem_scholarship,
        category='additional',
        description='Willingness to present findings at the end-of-year symposium',
        notes='Presentation can be poster or oral format',
        order=1
    )
    
    print(f"\n✅ Successfully added {stem_scholarship.requirements.count()} requirements!")
    print("\nRequirements by category:")
    
    for category in ['academic', 'documentation', 'eligibility', 'additional']:
        reqs = stem_scholarship.requirements.filter(category=category)
        if reqs.exists():
            print(f"\n{category.upper()}:")
            for req in reqs:
                print(f"  - {req.description}")
                if req.notes:
                    print(f"    Note: {req.notes}")
else:
    print("❌ STEM scholarship not found!")
