# Dynamic Document Requirements Feature

## Overview
This feature allows administrators to dynamically add new document requirements while creating a scholarship, without needing to pre-configure them in the admin panel.

## What Was Implemented

### 1. Frontend Changes (`templates/admin/create_scholarship.html`)

#### Added UI Components:
- **"Add New Requirement" Button**: Allows admins to add custom document requirements on the fly
- **Dynamic Requirement Cards**: Each new requirement appears as a card with the following fields:
  - Document Type (dropdown with predefined choices)
  - Custom Document Name (appears when "Other" is selected)
  - Description/Instructions (optional)
  - Allowed File Formats (e.g., PDF, DOC, DOCX)
  - Max File Size (in MB)
  - Is Required checkbox

#### Interactive Features:
- **Smooth Animations**: Cards slide in when added and fade out when removed
- **Conditional Fields**: Custom name field only shows when "Other" document type is selected
- **Remove Button**: Each card has an X button to remove it
- **Auto-scroll**: Automatically scrolls to newly added requirements
- **Empty State**: Shows helpful message when no requirements exist

### 2. Backend Changes (`core/views.py`)

#### Updated `create_scholarship` View:
- Processes dynamically added requirements from POST data
- Creates new `DocumentRequirement` objects on the fly
- Automatically associates them with the scholarship
- Handles validation for custom names when "Other" type is selected

#### Processing Logic:
```python
# Iterates through numbered fields (new_doc_type_1, new_doc_type_2, etc.)
# Creates DocumentRequirement objects
# Adds them to the scholarship's document_requirements many-to-many field
```

## How to Use

### For Administrators:

1. **Navigate to Create Scholarship page**
2. **Fill in basic scholarship information** (title, amount, deadline, etc.)
3. **Select existing document requirements** from checkboxes (if any exist)
4. **Click "Add New Requirement"** button to add custom requirements
5. **Fill in the requirement details**:
   - Select document type from dropdown
   - If "Other" is selected, provide a custom name
   - Add optional description/instructions
   - Specify allowed file formats
   - Set maximum file size
   - Check/uncheck if required
6. **Add multiple requirements** by clicking the button multiple times
7. **Remove unwanted requirements** by clicking the X button
8. **Submit the form** - all requirements (existing + new) will be saved

### Example Use Cases:

1. **Scholarship-Specific Documents**:
   - Create a scholarship requiring a "Research Proposal" (Other type)
   - Add custom instructions like "Must be 5-10 pages"

2. **Special Requirements**:
   - Add "Portfolio" for art scholarships
   - Add "Athletic Records" for sports scholarships
   - Add "Community Service Certificate" for service-based scholarships

3. **Quick Setup**:
   - No need to go to document requirements management first
   - Create everything in one place while setting up the scholarship

## Technical Details

### Document Type Choices:
- Certificate of Enrollment
- Certificate of Grades
- Certificate of Indigency
- Birth Certificate
- Barangay Clearance
- Police Clearance
- Medical Certificate
- Letter of Recommendation
- Essay/Personal Statement
- Official Transcript
- Tax Return/ITR
- Payslip/Income Certificate
- **Other Document** (with custom name)

### Field Naming Convention:
Dynamic fields use numbered suffixes:
- `new_doc_type_1`, `new_doc_type_2`, etc.
- `new_doc_custom_name_1`, `new_doc_custom_name_2`, etc.
- `new_doc_description_1`, `new_doc_description_2`, etc.
- `new_doc_formats_1`, `new_doc_formats_2`, etc.
- `new_doc_max_size_1`, `new_doc_max_size_2`, etc.
- `new_doc_required_1`, `new_doc_required_2`, etc.

### Validation:
- Document type is required
- Custom name is required when "Other" type is selected
- File formats default to "PDF, DOC, DOCX, JPG, PNG"
- Max file size defaults to 5MB (range: 1-50MB)
- Requirements are created in the database before being associated with the scholarship

## Benefits

1. **Streamlined Workflow**: Create scholarships and requirements in one place
2. **Flexibility**: Add scholarship-specific requirements without cluttering the global requirements list
3. **User-Friendly**: Intuitive UI with clear visual feedback
4. **Reusable**: Newly created requirements become available for future scholarships
5. **No Data Loss**: Requirements are saved to the database and can be reused

## Future Enhancements (Optional)

- Add ability to edit existing requirements inline
- Implement drag-and-drop reordering
- Add requirement templates for common scholarship types
- Include file preview/upload during requirement creation
- Add bulk import from CSV/Excel
