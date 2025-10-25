# Campus Selection - Quick Setup Guide

## Step 1: Apply Database Migration

Run the migration script to add the campus field to your database:

```bash
python add_campus_field_migration.py
```

This will:
- Create a new migration file
- Apply the migration to add the `campus` field to `UserProfile`
- Display success confirmation

## Step 2: Verify the Changes

Check that everything is working:

```bash
# Verify migrations are applied
python manage.py showmigrations core

# Start the development server
python manage.py runserver
```

## Step 3: Test Student Registration

1. Open your browser and go to the registration page
2. Select "Student" as account type
3. You should now see a "Campus" dropdown with three options:
   - Dumingag Campus
   - Mati Campus
   - Canuto Campus
4. Try registering without selecting a campus (should show validation error)
5. Complete registration with a campus selected

## Step 4: Test Admin Filtering

1. Login as an administrator
2. Go to "Pending Final Approvals" page
3. You should see a new "Campus" filter dropdown
4. Select a campus to filter applications
5. Verify that student campus information is displayed in application cards

## Step 5: Update Existing Students (Optional)

If you have existing student accounts without campus information:

### Option A: Manual Update via Admin Panel
1. Go to Django admin panel (`/admin`)
2. Navigate to User Profiles
3. Edit each student profile to add their campus

### Option B: Bulk Update Script

Create a script to update existing students:

```python
# update_student_campuses.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from core.models import UserProfile

# Example: Update specific students
students_to_update = [
    {'student_id': '2024001', 'campus': 'dumingag'},
    {'student_id': '2024002', 'campus': 'mati'},
    {'student_id': '2024003', 'campus': 'canuto'},
]

for student_data in students_to_update:
    try:
        profile = UserProfile.objects.get(student_id=student_data['student_id'])
        profile.campus = student_data['campus']
        profile.save()
        print(f"✓ Updated {profile.user.get_full_name()} - {student_data['campus']}")
    except UserProfile.DoesNotExist:
        print(f"✗ Student ID {student_data['student_id']} not found")

print("\nDone!")
```

Run it:
```bash
python update_student_campuses.py
```

## Troubleshooting

### Issue: Migration fails
**Solution:** Make sure you're in the project directory and Django settings are correct

### Issue: Campus field not showing in registration
**Solution:** 
- Clear browser cache
- Check that `core/forms.py` has the campus field
- Verify template changes in `templates/auth/register.html`

### Issue: Campus filter not working in admin view
**Solution:**
- Check that `core/views_admin_approval.py` includes campus filtering logic
- Verify `campus_choices` is passed in context
- Check template has the campus dropdown

### Issue: Existing students can't apply for scholarships
**Solution:** Students need to update their profile to add campus information

## Adding More Campuses

To add additional campuses in the future:

1. Edit `core/models.py`:
```python
CAMPUS_CHOICES = [
    ('dumingag', 'Dumingag Campus'),
    ('mati', 'Mati Campus'),
    ('canuto', 'Canuto Campus'),
    ('new_campus', 'New Campus Name'),  # Add here
]
```

2. No migration needed (CharField with choices doesn't require migration for choice changes)

3. New campus will appear in all dropdowns automatically

## Next Steps

After setup is complete:

1. ✅ Test student registration with campus selection
2. ✅ Test admin filtering by campus
3. ✅ Update existing student profiles with campus information
4. ✅ Train staff on using the campus filter
5. ✅ Consider campus-specific scholarship programs

## Support

If you encounter any issues:
1. Check the main documentation: `CAMPUS_SELECTION_FEATURE.md`
2. Verify all files were updated correctly
3. Check Django logs for errors
4. Ensure database migrations are applied
