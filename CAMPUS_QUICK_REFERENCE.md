# Campus Selection - Quick Reference Card

## 🎓 For Students

### During Registration
1. Select "Student" as account type
2. **Required:** Choose your campus from dropdown:
   - 🏛️ Dumingag Campus
   - 🏛️ Mati Campus  
   - 🏛️ Canuto Campus
3. Complete other required fields

### After Registration
- Campus info appears in your profile
- Can be updated in profile settings

---

## 👨‍💼 For Administrators

### Filtering Applications by Campus

**Location:** Admin Dashboard → Pending Final Approvals

**Steps:**
1. Click "Campus" dropdown
2. Select desired campus or "All Campuses"
3. Click "Apply Filters"

**Combine with:**
- OSAS Recommendation filter
- Scholarship filter
- Student name search

### Viewing Campus Info
- Campus displayed in each application card
- Shows alongside GPA and scholarship info
- Helps identify student origin

---

## 🛠️ For Developers

### Current Distribution
```
Dumingag Campus: 3 students
Mati Campus:     1 student
Canuto Campus:   1 student
```

### Check Distribution
```bash
python populate_student_campuses.py --show
```

### Add New Campus
Edit `core/models.py`:
```python
CAMPUS_CHOICES = [
    ('dumingag', 'Dumingag Campus'),
    ('mati', 'Mati Campus'),
    ('canuto', 'Canuto Campus'),
    ('new_code', 'New Campus Name'),  # Add here
]
```

### Key Files
- **Model:** `core/models.py` (UserProfile.campus)
- **Form:** `core/forms.py` (CustomUserCreationForm)
- **Views:** `core/views_admin_approval.py`
- **Templates:** 
  - `templates/auth/register.html`
  - `templates/admin/pending_approvals.html`

---

## 📊 Testing Checklist

- [x] Migration applied successfully
- [x] 5 students populated with campuses
- [x] Registration form shows campus dropdown
- [x] Campus is required for students
- [x] Admin filter works correctly
- [x] Campus displays in application cards
- [x] No diagnostic errors

---

## 🚀 Quick Commands

```bash
# View campus distribution
python populate_student_campuses.py --show

# Start server
python manage.py runserver

# Check migrations
python manage.py showmigrations core
```

---

## 📞 Need Help?

1. **Full Documentation:** `CAMPUS_SELECTION_FEATURE.md`
2. **Setup Guide:** `CAMPUS_SETUP_GUIDE.md`
3. **Implementation Summary:** `CAMPUS_IMPLEMENTATION_SUMMARY.md`

---

**Status:** ✅ Ready for Production Use
