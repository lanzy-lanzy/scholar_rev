# AJAX Dynamic Requirements - Flow Diagram

## 🔄 Complete Flow Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                    CREATE SCHOLARSHIP PAGE                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Basic Info: Title, Amount, Deadline, etc.         │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  EXISTING REQUIREMENTS (Checkbox List)             │    │
│  │  ☑ Certificate of Enrollment                       │    │
│  │  ☑ Certificate of Grades                           │    │
│  │  ☐ Birth Certificate                               │    │
│  │  ☐ Transcript                                      │    │
│  │                                                     │    │
│  │  [+ Add New Requirement] ← CLICK HERE              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    USER CLICKS BUTTON
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              BLUE CREATION FORM APPEARS                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Create New Document Requirement            [X]    │    │
│  │                                                     │    │
│  │  Document Type: [Other Document ▼]                 │    │
│  │  Custom Name: [Art Portfolio____________]          │    │
│  │  Description: [Submit 5-10 samples_____]           │    │
│  │  Formats: [PDF, JPG, PNG_______________]           │    │
│  │  Max Size: [10] MB                                 │    │
│  │  ☑ This document is required                       │    │
│  │                                                     │    │
│  │           [Cancel]  [Save & Add to List]           │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
                USER CLICKS "SAVE & ADD TO LIST"
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    AJAX REQUEST                              │
│                                                              │
│  JavaScript collects form data:                             │
│  {                                                           │
│    doc_type: "other",                                       │
│    custom_name: "Art Portfolio",                            │
│    description: "Submit 5-10 samples...",                   │
│    formats: "PDF, JPG, PNG",                                │
│    max_size: "10",                                          │
│    is_required: true                                        │
│  }                                                           │
│                                                              │
│  POST → /ajax/create-document-requirement/                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DJANGO BACKEND                              │
│                                                              │
│  @login_required                                            │
│  def ajax_create_document_requirement(request):             │
│      # Validate admin access                                │
│      # Extract POST data                                    │
│      # Validate required fields                             │
│                                                              │
│      doc_req = DocumentRequirement.objects.create(          │
│          name='other',                                      │
│          custom_name='Art Portfolio',                       │
│          description='Submit 5-10 samples...',              │
│          file_format_requirements='PDF, JPG, PNG',          │
│          max_file_size_mb=10,                               │
│          is_required=True                                   │
│      )                                                       │
│                                                              │
│      return JsonResponse({                                  │
│          'success': True,                                   │
│          'requirement': {                                   │
│              'id': 42,                                      │
│              'display_name': 'Art Portfolio',               │
│              'description': '...',                          │
│              ...                                            │
│          }                                                   │
│      })                                                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE                                  │
│                                                              │
│  INSERT INTO core_documentrequirement                       │
│  (name, custom_name, description, ...)                      │
│  VALUES ('other', 'Art Portfolio', '...', ...)              │
│                                                              │
│  → New record created with ID: 42                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              JAVASCRIPT RECEIVES RESPONSE                    │
│                                                              │
│  .then(data => {                                            │
│      if (data.success) {                                    │
│          // Create checkbox element                         │
│          // Add to existing requirements list               │
│          // Auto-check it                                   │
│          // Show success notification                       │
│          // Remove creation form                            │
│      }                                                       │
│  })                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            UPDATED REQUIREMENTS LIST                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │  EXISTING REQUIREMENTS                             │    │
│  │  ☑ Certificate of Enrollment                       │    │
│  │  ☑ Certificate of Grades                           │    │
│  │  ☐ Birth Certificate                               │    │
│  │  ☐ Transcript                                      │    │
│  │                                                     │    │
│  │  ☑ Art Portfolio [New] ← NEWLY CREATED!            │    │
│  │    Submit 5-10 samples of your best artwork        │    │
│  │                                                     │    │
│  │  [+ Add New Requirement]                           │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  ✓ Requirement "Art Portfolio" created!            │    │
│  └────────────────────────────────────────────────────┘    │
│         ↑ Success notification (auto-dismisses)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
                  USER CONTINUES CREATING SCHOLARSHIP
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              SUBMIT SCHOLARSHIP FORM                         │
│                                                              │
│  Selected requirements:                                     │
│  - Certificate of Enrollment (ID: 1)                        │
│  - Certificate of Grades (ID: 2)                            │
│  - Art Portfolio (ID: 42) ← NEW ONE INCLUDED!               │
│                                                              │
│  POST → /dashboard/admin/scholarships/create/               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            SCHOLARSHIP CREATED IN DATABASE                   │
│                                                              │
│  Scholarship:                                               │
│  - Title: "Art Excellence Scholarship"                      │
│  - Amount: ₱50,000                                          │
│  - ...                                                       │
│                                                              │
│  Associated Requirements (Many-to-Many):                    │
│  - DocumentRequirement ID: 1                                │
│  - DocumentRequirement ID: 2                                │
│  - DocumentRequirement ID: 42 ← NEW ONE!                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    SUCCESS!                                  │
│                                                              │
│  ✓ Scholarship created                                      │
│  ✓ Requirements associated                                  │
│  ✓ "Art Portfolio" now available for future scholarships!   │
└─────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════
                    FUTURE SCHOLARSHIP
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│         CREATING ANOTHER ART SCHOLARSHIP                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  EXISTING REQUIREMENTS                             │    │
│  │  ☑ Certificate of Enrollment                       │    │
│  │  ☑ Certificate of Grades                           │    │
│  │  ☐ Birth Certificate                               │    │
│  │  ☐ Transcript                                      │    │
│  │  ☑ Art Portfolio ← JUST CHECK IT!                  │    │
│  │    Submit 5-10 samples of your best artwork        │    │
│  │                                                     │    │
│  │  [+ Add New Requirement]                           │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  NO NEED TO RECREATE! Just select from list! 🎉            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Points

### 1. **Immediate Creation**
- Requirement created via AJAX **before** scholarship submission
- Saved to database instantly
- No waiting until form submit

### 2. **Visual Feedback**
- Blue form = creation mode
- Green highlight = newly created
- Success notification = confirmation
- "New" badge = easy identification

### 3. **Automatic Selection**
- Newly created requirements are auto-checked
- Included in current scholarship
- Can be unchecked if needed

### 4. **Permanent Availability**
- Once created, always available
- Shows up in all future scholarship forms
- Build a library over time

---

## 📊 Data Flow

```
Frontend (JavaScript)
    ↓ AJAX POST
Backend (Django View)
    ↓ Create Object
Database (PostgreSQL/SQLite)
    ↓ Return ID
Backend (JSON Response)
    ↓ Send Data
Frontend (Update UI)
    ↓ Add Checkbox
User (See Result)
```

---

## 🎯 Comparison: Before vs After

### BEFORE (Old Approach):
```
Create Form → Fill Details → Submit Scholarship
                                    ↓
                            Create Requirements
                                    ↓
                            Associate with Scholarship
                                    ↓
                            NOT REUSABLE (must recreate)
```

### AFTER (New Approach):
```
Create Form → Fill Details → Click "Save & Add"
                                    ↓
                            AJAX Creates Requirement
                                    ↓
                            Appears in Checkbox List
                                    ↓
                            Auto-Selected
                                    ↓
Submit Scholarship → Associate Selected Requirements
                                    ↓
                            REUSABLE FOREVER! ✨
```

---

## 🚀 Performance

- **AJAX Request**: ~100-300ms
- **Database Insert**: ~10-50ms
- **UI Update**: Instant
- **Total Time**: < 1 second
- **User Experience**: Seamless!

---

## 🎨 Visual States

### State 1: Initial
- Existing requirements shown as checkboxes
- "Add New Requirement" button visible

### State 2: Creating
- Blue form appears
- Fields ready for input
- Cancel and Save buttons

### State 3: Saving
- Save button shows spinner
- "Saving..." text
- Button disabled

### State 4: Success
- Form disappears
- New checkbox appears (green)
- Success notification (top-right)
- Auto-checked

### State 5: Ready
- New requirement in list
- Available for selection
- Can be used immediately

---

This flow ensures that **every requirement you create is immediately available for reuse**, eliminating the need to recreate common requirements! 🎉
