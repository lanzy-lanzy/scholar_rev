# Custom Document Requirements Implementation

## Overview
The scholarship system now supports dynamic custom document requirements that persist in the database and become available for future scholarships.

## How It Works

### 1. Creating Custom Documents
When creating or editing a scholarship, admins can:
- Select from **Standard Documents** (pre-existing in database)
- Add **Custom Documents** dynamically using the "Add Custom Document" button

### 2. Custom Document Fields
Each custom document includes:
- **Document Name** (required) - e.g., "Letter of Recommendation"
- **File Formats** - Accepted formats (default: PDF, DOC, DOCX)
- **Max Size (MB)** - Maximum file size (default: 10MB)
- **Required** - Checkbox to mark as required/optional
- **Description** - Optional instructions for students

### 3. Database Persistence
When a custom document is added:
1. A new `DocumentRequirement` object is created with `name='other'`
2. The custom name is stored in the `custom_name` field
3. The document is automatically added to the scholarship's `document_requirements`
4. **The document becomes available for ALL future scholarships**

### 4. Visual Design
- **Standard documents**: Green highlight when selected
- **Custom documents**: Yellow/gold styling to differentiate
- Smooth animations for adding/removing items
- Remove button with rotation animation

## Backend Implementation

### Views (core/views.py)
Both `create_scholarship` and `edit_scholarship` views now:
1. Parse POST data for custom document fields (pattern: `custom_document_name_*`)
2. Create `DocumentRequirement` objects for each custom document
3. Associate them with the scholarship via many-to-many relationship

### Models (core/models.py)
The `DocumentRequirement` model supports:
- `name='other'` for custom documents
- `custom_name` field for the actual document name
- `display_name` property that returns custom_name when name is 'other'

### Forms (core/forms.py)
The `ScholarshipForm` includes:
- `document_requirements` as a `ModelMultipleChoiceField`
- Displays all existing DocumentRequirement objects as checkboxes

## Usage Flow

### For Admins Creating Scholarships:
1. Navigate to Create/Edit Scholarship
2. Select standard documents from checkboxes
3. Click "Add Custom Document" for additional requirements
4. Fill in custom document details
5. Submit form
6. Custom documents are saved to database and associated with scholarship

### For Future Scholarships:
1. Previously created custom documents appear in the "Standard Documents" section
2. Can be selected like any other document requirement
3. No need to recreate common custom documents

## Example Scenario
1. Admin creates "Merit Scholarship" and adds custom document "Faculty Recommendation Letter"
2. Document is saved to database
3. Later, when creating "Excellence Scholarship", the "Faculty Recommendation Letter" appears as a standard option
4. Admin can select it without recreating it

## Benefits
- **Reusability**: Create once, use many times
- **Consistency**: Same document requirements across scholarships
- **Flexibility**: Can still add new custom documents anytime
- **Organization**: Clear separation between standard and custom documents
