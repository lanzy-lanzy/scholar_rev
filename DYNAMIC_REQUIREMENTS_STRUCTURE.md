# Dynamic Requirements - HTML Structure Reference

## Component Hierarchy

```
Document Requirements Section
│
├── Header Row
│   ├── Description Text
│   └── "Add New Requirement" Button (id: addRequirementBtn)
│
├── Existing Requirements Grid (id: existingRequirements)
│   ├── Checkbox Items (from form.document_requirements)
│   └── Empty State (id: emptyState) [shown when no requirements]
│
└── Dynamic Requirements Container (id: dynamicRequirements)
    └── Requirement Cards (dynamically added)
        ├── Card Header
        │   ├── Title: "New Document Requirement"
        │   └── Remove Button (X icon)
        │
        └── Card Body
            ├── Document Type Dropdown
            ├── Custom Name Input (conditional)
            ├── Description Textarea
            ├── File Formats Input
            ├── Max File Size Input
            └── Is Required Checkbox
```

---

## Field Naming Convention

Each dynamically added requirement uses numbered fields:

```javascript
// Counter increments with each new requirement
requirementCounter = 1, 2, 3, ...

// Field names follow this pattern:
new_doc_type_{counter}           // e.g., new_doc_type_1
new_doc_custom_name_{counter}    // e.g., new_doc_custom_name_1
new_doc_description_{counter}    // e.g., new_doc_description_1
new_doc_formats_{counter}        // e.g., new_doc_formats_1
new_doc_max_size_{counter}       // e.g., new_doc_max_size_1
new_doc_required_{counter}       // e.g., new_doc_required_1 (checkbox)
```

---

## HTML Structure of Dynamic Card

```html
<div class="border-2 border-gray-300 rounded-xl p-6 bg-white shadow-sm animate-slide-up" 
     id="new_requirement_{counter}">
    
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
        <h4 class="text-lg font-bold" style="color: var(--primary-dark);">
            New Document Requirement
        </h4>
        <button type="button" 
                class="remove-requirement text-red-600 hover:text-red-800 transition-colors" 
                data-id="new_requirement_{counter}">
            <svg class="w-6 h-6"><!-- X icon --></svg>
        </button>
    </div>
    
    <!-- Body -->
    <div class="space-y-4">
        
        <!-- Document Type -->
        <div>
            <label class="block text-sm font-bold mb-2">Document Type *</label>
            <select name="new_doc_type_{counter}" 
                    class="form-input w-full border rounded-lg" 
                    required>
                <option value="">Select document type...</option>
                <option value="certificate_enrollment">Certificate of Enrollment</option>
                <!-- ... more options ... -->
                <option value="other">Other Document</option>
            </select>
        </div>
        
        <!-- Custom Name (hidden by default) -->
        <div class="custom-name-field" style="display: none;">
            <label class="block text-sm font-bold mb-2">Custom Document Name *</label>
            <input type="text" 
                   name="new_doc_custom_name_{counter}" 
                   class="form-input w-full border rounded-lg" 
                   placeholder="Enter custom document name">
        </div>
        
        <!-- Description -->
        <div>
            <label class="block text-sm font-bold mb-2">Description/Instructions</label>
            <textarea name="new_doc_description_{counter}" 
                      class="form-input w-full border rounded-lg" 
                      rows="2" 
                      placeholder="Additional instructions for this document"></textarea>
        </div>
        
        <!-- File Formats & Max Size (Grid) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <!-- File Formats -->
            <div>
                <label class="block text-sm font-bold mb-2">Allowed File Formats *</label>
                <input type="text" 
                       name="new_doc_formats_{counter}" 
                       class="form-input w-full border rounded-lg" 
                       value="PDF, DOC, DOCX, JPG, PNG" 
                       required>
            </div>
            
            <!-- Max File Size -->
            <div>
                <label class="block text-sm font-bold mb-2">Max File Size (MB) *</label>
                <input type="number" 
                       name="new_doc_max_size_{counter}" 
                       class="form-input w-full border rounded-lg" 
                       value="5" 
                       min="1" 
                       max="50" 
                       required>
            </div>
        </div>
        
        <!-- Is Required Checkbox -->
        <div class="flex items-center">
            <input type="checkbox" 
                   name="new_doc_required_{counter}" 
                   id="new_doc_required_{counter}" 
                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" 
                   checked>
            <label for="new_doc_required_{counter}" 
                   class="ml-2 text-sm font-medium">
                This document is required
            </label>
        </div>
        
    </div>
</div>
```

---

## JavaScript Event Handlers

### Add Requirement Button
```javascript
addRequirementBtn.addEventListener('click', function() {
    // 1. Hide empty state if visible
    // 2. Increment counter
    // 3. Create new card element
    // 4. Append to dynamicRequirements container
    // 5. Attach event listeners (type change, remove)
    // 6. Scroll to new card
});
```

### Document Type Change
```javascript
typeSelect.addEventListener('change', function() {
    if (this.value === 'other') {
        // Show custom name field
        // Make it required
    } else {
        // Hide custom name field
        // Make it optional
        // Clear value
    }
});
```

### Remove Button
```javascript
removeBtn.addEventListener('click', function() {
    // 1. Add fade-out animation class
    // 2. Wait for animation (300ms)
    // 3. Remove card from DOM
    // 4. Show empty state if no requirements left
});
```

---

## CSS Classes Used

### Layout Classes
- `border-2 border-gray-300` - Card border
- `rounded-xl` - Rounded corners
- `p-6` - Padding
- `bg-white` - White background
- `shadow-sm` - Subtle shadow
- `space-y-4` - Vertical spacing between elements
- `grid grid-cols-1 md:grid-cols-2 gap-4` - Responsive grid

### Animation Classes
- `animate-slide-up` - Slide in animation (custom)
- `animate-fade-out` - Fade out animation (custom)
- `transition-colors` - Smooth color transitions

### Form Classes
- `form-input` - Base input styling
- `w-full` - Full width
- `border rounded-lg` - Border and rounded corners

### Color Classes
- `text-red-600 hover:text-red-800` - Remove button colors
- `text-indigo-600` - Checkbox color
- `border-gray-300` - Border color

---

## Data Flow

### Form Submission
```
User fills form → Submit button clicked
    ↓
POST data includes:
{
    'title': 'Scholarship Title',
    'description': '...',
    // ... other scholarship fields ...
    'document_requirements': [1, 2, 3],  // Existing requirements
    'new_doc_type_1': 'other',
    'new_doc_custom_name_1': 'Portfolio',
    'new_doc_description_1': '...',
    'new_doc_formats_1': 'PDF, JPG, PNG',
    'new_doc_max_size_1': '10',
    'new_doc_required_1': 'on',
    'new_doc_type_2': 'recommendation_letter',
    // ... more dynamic fields ...
}
    ↓
Django view processes data
    ↓
Creates DocumentRequirement objects
    ↓
Associates with Scholarship
    ↓
Redirects to success page
```

---

## State Management

### JavaScript Variables
```javascript
let requirementCounter = 0;              // Tracks number of requirements added
const addRequirementBtn = ...;           // Button element
const dynamicRequirements = ...;         // Container element
const existingRequirements = ...;        // Existing requirements grid
const emptyState = ...;                  // Empty state element
const documentTypes = [...];             // Array of document type options
```

### DOM State
- **Empty State**: Shown when no requirements exist (existing or dynamic)
- **Card Count**: Tracked by number of children in `dynamicRequirements`
- **Field Values**: Stored in input elements, submitted with form

---

## Validation

### Frontend Validation
- Document type: Required (HTML5 `required` attribute)
- Custom name: Required only when "Other" is selected (dynamic)
- File formats: Required (HTML5 `required` attribute)
- Max file size: Required, min=1, max=50 (HTML5 validation)

### Backend Validation
- Checks if document type exists in POST data
- Validates custom name for "Other" type
- Sanitizes and validates file size (converts to int)
- Handles checkbox state (presence = checked)

---

## Accessibility Features

- ✅ Proper label associations (`for` attribute)
- ✅ Required fields marked with asterisk (*)
- ✅ Semantic HTML structure
- ✅ Keyboard navigation support
- ✅ Focus states on interactive elements
- ✅ ARIA labels could be added for screen readers (future enhancement)

---

## Browser Compatibility

- ✅ Modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ CSS Grid support required
- ✅ ES6 JavaScript features (arrow functions, template literals)
- ✅ HTML5 form validation
- ✅ CSS animations and transitions

---

## Performance Considerations

- **Efficient DOM manipulation**: Cards created once, not repeatedly
- **Event delegation**: Could be improved by using delegation on container
- **Animation performance**: CSS animations use transform (GPU accelerated)
- **Memory management**: Event listeners properly attached to new elements
- **Scalability**: No limit on number of requirements (reasonable usage expected)

---

## Maintenance Notes

### To Add New Document Type:
1. Add to `DOCUMENT_TYPE_CHOICES` in `models.py`
2. Add to `documentTypes` array in JavaScript
3. No other changes needed (fully dynamic)

### To Modify Card Layout:
1. Update template literal in JavaScript
2. Adjust CSS classes as needed
3. Ensure field naming convention is maintained

### To Change Validation Rules:
1. Update HTML5 attributes (min, max, required)
2. Update backend validation in `create_scholarship` view
3. Update JavaScript conditional logic if needed

---

This structure provides a flexible, maintainable, and user-friendly system for managing dynamic document requirements in the scholarship creation process.
