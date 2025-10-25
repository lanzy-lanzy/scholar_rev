# Campus Selection Feature Implementation

## Overview
This feature allows students to select their campus during registration (Dumingag Campus, Mati Campus, or Canuto Campus) and enables administrators to filter scholarship applications by campus for better management and approval workflows.

## Changes Made

### 1. Database Model Updates (`core/models.py`)

Added a new `campus` field to the `UserProfile` model:

```python
CAMPUS_CHOICES = [
    ('dumingag', 'Dumingag Campus'),
    ('mati', 'Mati Campus'),
    ('canuto', 'Canuto Campus'),
]

campus = models.CharField(
    max_length=20, 
    choices=CAMPUS_CHOICES, 
    null=True, 
    blank=True, 
    help_text='Select your campus'
)
```

### 2. Registration Form Updates (`core/forms.py`)

#### CustomUserCreationForm
- Added `campus` field with dropdown selection
- Made campus **required** for students during registration
- Added validation to ensure students provide their campus

#### UserProfileForm
- Added `campus` field to profile update form
- Allows students to update their campus information later

### 3. Registration Template (`templates/auth/register.html`)

Added campus selection field in the Student Information section:
- Appears only when user selects "Student" as account type
- Dropdown with three campus options
- Required field with validation
- Styled consistently with other form fields

### 4. Admin Views (`core/views_admin_approval.py`)

Enhanced admin approval views with campus filtering:

#### `admin_pending_approvals` view
- Added campus filter parameter
- Filters applications by student's campus
- Shows campus information in application list

#### `admin_review_history` view
- Added campus filter for historical review data
- Allows admins to view decisions by campus

### 5. Admin Templates

#### `templates/admin/pending_approvals.html`
- Added campus dropdown filter
- Displays student's campus in application details
- Filter persists across pagination

## How to Use

### For Students

1. **During Registration:**
   - Select "Student" as account type
   - Fill in Student ID
   - **Select your campus** from the dropdown:
     - Dumingag Campus
     - Mati Campus
     - Canuto Campus
   - Select your year level
   - Complete other required fields

2. **After Registration:**
   - Campus information appears in your profile
   - Can be updated from profile settings

### For Administrators

1. **Filtering Applications by Campus:**
   - Go to "Pending Final Approvals" page
   - Use the "Campus" dropdown filter
   - Select specific campus or view "All Campuses"
   - Combine with other filters (scholarship, OSAS recommendation)

2. **Viewing Campus Information:**
   - Each application card shows the student's campus
   - Campus is displayed alongside scholarship and GPA information
   - Helps identify student origin for approval decisions

3. **Review History:**
   - Filter historical decisions by campus
   - Track approval patterns per campus
   - Generate campus-specific reports

## Database Migration

To apply the campus field to your database:

```bash
# Run the migration script
python add_campus_field_migration.py
```

Or manually:

```bash
# Create migration
python manage.py makemigrations core

# Apply migration
python manage.py migrate
```

## Benefits

1. **Better Organization:** Admins can easily identify and filter students by their campus origin
2. **Targeted Approvals:** Campus-specific scholarship programs can be managed more efficiently
3. **Reporting:** Generate campus-wise statistics and reports
4. **Accountability:** Track which campus students are receiving scholarships
5. **Scalability:** Easy to add more campuses in the future

## Future Enhancements

Potential improvements for this feature:

1. **Campus-Specific Scholarships:** Create scholarships available only to specific campuses
2. **Campus Admins:** Assign admin roles per campus for decentralized management
3. **Campus Statistics:** Dashboard showing application and approval rates per campus
4. **Campus Quotas:** Set scholarship slot limits per campus
5. **Multi-Campus Support:** Allow students to indicate multiple campus affiliations

## Technical Notes

- Campus field is optional for non-student users (admin, OSAS staff)
- Existing student records will have `null` campus until updated
- Campus choices are defined in `UserProfile.CAMPUS_CHOICES`
- To add new campuses, update the `CAMPUS_CHOICES` tuple in `models.py`

## Testing

Test the feature with these scenarios:

1. **New Student Registration:**
   - Register as student without selecting campus (should show error)
   - Register with campus selected (should succeed)

2. **Admin Filtering:**
   - Create applications from students of different campuses
   - Test campus filter on pending approvals page
   - Verify campus displays correctly in application details

3. **Profile Updates:**
   - Update student profile to change campus
   - Verify changes reflect in admin views

## Support

For issues or questions about this feature:
- Check that migrations are applied: `python manage.py showmigrations core`
- Verify campus choices in `core/models.py`
- Ensure templates are properly loaded
- Check admin view context includes `campus_choices` and `campus_filter`
