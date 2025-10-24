# Dynamic Requirements - Quick Reference Card

## 🚀 Quick Start

### For Administrators (Users):
1. Go to **Create Scholarship** page
2. Click **"Add New Requirement"** button
3. Fill in requirement details
4. Click **"Add New Requirement"** again for more
5. Click **X** to remove unwanted requirements
6. Submit form

### For Developers:
```javascript
// Frontend: templates/admin/create_scholarship.html
// Backend: core/views.py (create_scholarship function)
// Tests: core/tests.py (DynamicRequirementsTest class)
```

---

## 📦 Files Modified

| File | Changes |
|------|---------|
| `templates/admin/create_scholarship.html` | Added dynamic UI, JavaScript logic |
| `core/views.py` | Updated `create_scholarship` to process dynamic fields |
| `core/tests.py` | Added `DynamicRequirementsTest` class |

---

## 🎯 Key Components

### HTML Elements
```html
<button id="addRequirementBtn">Add New Requirement</button>
<div id="existingRequirements"><!-- Existing checkboxes --></div>
<div id="dynamicRequirements"><!-- Dynamic cards --></div>
<div id="emptyState"><!-- Shown when no requirements --></div>
```

### JavaScript Variables
```javascript
let requirementCounter = 0;
const documentTypes = [/* 13 predefined types */];
```

### Field Names
```
new_doc_type_{counter}
new_doc_custom_name_{counter}
new_doc_description_{counter}
new_doc_formats_{counter}
new_doc_max_size_{counter}
new_doc_required_{counter}
```

---

## 🔧 Backend Processing

```python
# In create_scholarship view
counter = 1
while f'new_doc_type_{counter}' in request.POST:
    # Extract data
    doc_type = request.POST.get(f'new_doc_type_{counter}')
    custom_name = request.POST.get(f'new_doc_custom_name_{counter}', '')
    # ... more fields ...
    
    # Create DocumentRequirement
    doc_req = DocumentRequirement.objects.create(...)
    
    # Add to scholarship
    scholarship.document_requirements.add(doc_req)
    
    counter += 1
```

---

## 📋 Document Types

1. `certificate_enrollment` - Certificate of Enrollment
2. `certificate_grades` - Certificate of Grades
3. `certificate_indigency` - Certificate of Indigency
4. `birth_certificate` - Birth Certificate
5. `barangay_clearance` - Barangay Clearance
6. `police_clearance` - Police Clearance
7. `medical_certificate` - Medical Certificate
8. `recommendation_letter` - Letter of Recommendation
9. `essay` - Essay/Personal Statement
10. `transcript` - Official Transcript
11. `tax_return` - Tax Return/ITR
12. `payslip` - Payslip/Income Certificate
13. `other` - Other Document (requires custom_name)

---

## ✅ Validation Rules

| Field | Required | Validation |
|-------|----------|------------|
| Document Type | Yes | Must be from predefined list |
| Custom Name | Conditional | Required only if type = "other" |
| Description | No | Optional text |
| File Formats | Yes | Comma-separated list |
| Max File Size | Yes | 1-50 MB |
| Is Required | No | Checkbox (default: checked) |

---

## 🎨 CSS Classes

### Animations
```css
.animate-slide-up { /* Slide in from bottom */ }
.animate-fade-out { /* Fade out and move up */ }
```

### Layout
```css
.border-2 border-gray-300 rounded-xl p-6 bg-white shadow-sm
```

### Colors
```css
text-red-600 hover:text-red-800  /* Remove button */
text-indigo-600                   /* Checkbox */
```

---

## 🧪 Testing

### Run Tests
```powershell
python manage.py test core.tests.DynamicRequirementsTest
```

### Test Cases
1. ✅ Create scholarship with dynamic requirements
2. ✅ Create scholarship without dynamic requirements
3. ✅ Dynamic requirement with custom name

---

## 🐛 Common Issues

### Issue: Custom name field not showing
**Fix**: Ensure "Other Document" is selected in dropdown

### Issue: Requirements not saving
**Fix**: Check that form is being submitted (not just adding requirements)

### Issue: Validation errors
**Fix**: Ensure all required fields are filled

---

## 📊 Database Schema

```sql
-- DocumentRequirement Model
id                          INTEGER PRIMARY KEY
name                        VARCHAR(100)  -- Document type
custom_name                 VARCHAR(200)  -- For 'other' type
description                 TEXT
is_required                 BOOLEAN
file_format_requirements    VARCHAR(100)
max_file_size_mb           INTEGER

-- Scholarship-DocumentRequirement Relationship
scholarship_id              INTEGER (FK)
documentrequirement_id      INTEGER (FK)
```

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────┐
│  User clicks "Add New Requirement"      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  JavaScript creates new card            │
│  - Increments counter                   │
│  - Generates HTML                       │
│  - Attaches event listeners             │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  User fills in requirement details      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  User submits form                      │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Django view processes POST data        │
│  - Validates scholarship fields         │
│  - Saves scholarship                    │
│  - Processes dynamic requirements       │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Creates DocumentRequirement objects    │
│  - Iterates through numbered fields     │
│  - Creates DB records                   │
│  - Associates with scholarship          │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Redirects to Manage Scholarships       │
│  Shows success message                  │
└─────────────────────────────────────────┘
```

---

## 💡 Pro Tips

1. **Multiple Requirements**: Click "Add New Requirement" multiple times
2. **Reordering**: Requirements are displayed in the order they're added
3. **Reusability**: Created requirements become available for other scholarships
4. **Validation**: Fill all required fields before submitting
5. **Custom Names**: Be descriptive when using "Other" type

---

## 🔗 Related Files

- **Models**: `core/models.py` (DocumentRequirement, Scholarship)
- **Forms**: `core/forms.py` (ScholarshipForm)
- **Views**: `core/views.py` (create_scholarship, edit_scholarship)
- **URLs**: `core/urls.py` (scholarship routes)
- **Templates**: `templates/admin/create_scholarship.html`

---

## 📞 Support

For questions or issues:
1. Check documentation files (FEATURE_USAGE_GUIDE.md)
2. Review implementation summary (IMPLEMENTATION_SUMMARY.md)
3. Examine code structure (DYNAMIC_REQUIREMENTS_STRUCTURE.md)
4. Contact development team

---

## 🎓 Learning Resources

### JavaScript Concepts Used:
- DOM manipulation
- Event listeners
- Template literals
- Arrow functions
- Conditional rendering

### Django Concepts Used:
- POST data processing
- Model creation
- Many-to-many relationships
- Form handling
- Validation

### CSS Concepts Used:
- Flexbox layout
- Grid layout
- Animations
- Transitions
- Responsive design

---

**Version**: 1.0  
**Last Updated**: 2025-10-02  
**Status**: ✅ Production Ready
