# Dynamic Requirements - Usage Guide

## Visual Walkthrough

### Step 1: Create Scholarship Page
When you navigate to the Create Scholarship page, you'll see the Document Requirements section with:
- Existing document requirements (if any) displayed as checkboxes
- An "Add New Requirement" button at the top right

### Step 2: Click "Add New Requirement"
Clicking this button will:
- Display a new card with a smooth slide-down animation
- Show all fields needed to define a new document requirement
- Automatically scroll to the new card

### Step 3: Fill in Requirement Details

**Required Fields:**
- **Document Type**: Select from dropdown (Certificate of Enrollment, Birth Certificate, etc.)
- **Allowed File Formats**: Comma-separated list (defaults to "PDF, DOC, DOCX, JPG, PNG")
- **Max File Size (MB)**: Number between 1-50 (defaults to 5)

**Optional Fields:**
- **Description/Instructions**: Additional guidance for students
- **This document is required**: Checkbox (checked by default)

**Conditional Field:**
- **Custom Document Name**: Only appears when "Other Document" is selected

### Step 4: Add Multiple Requirements
You can click "Add New Requirement" multiple times to add as many custom requirements as needed. Each will be numbered internally (new_requirement_1, new_requirement_2, etc.)

### Step 5: Remove Unwanted Requirements
Each requirement card has an X button in the top-right corner. Clicking it will:
- Fade out the card with animation
- Remove it from the form
- Not affect the database until form submission

### Step 6: Submit the Form
When you submit the scholarship form:
1. All basic scholarship info is validated
2. Existing document requirements (checkboxes) are saved
3. New dynamic requirements are created in the database
4. All requirements are associated with the scholarship
5. You're redirected to the Manage Scholarships page

## Example Scenarios

### Scenario 1: Art Scholarship
**Existing Requirements:**
- ☑ Certificate of Enrollment
- ☑ Certificate of Grades

**New Requirements Added:**
1. **Portfolio**
   - Type: Other Document
   - Custom Name: "Art Portfolio"
   - Description: "Submit 5-10 samples of your best artwork"
   - Formats: PDF, JPG, PNG
   - Max Size: 10 MB
   - Required: Yes

2. **Artist Statement**
   - Type: Essay/Personal Statement
   - Description: "Describe your artistic vision and goals (500-1000 words)"
   - Formats: PDF, DOC, DOCX
   - Max Size: 5 MB
   - Required: Yes

### Scenario 2: Athletic Scholarship
**New Requirements Added:**
1. **Athletic Records**
   - Type: Other Document
   - Custom Name: "Athletic Performance Records"
   - Description: "Include competition results, awards, and statistics"
   - Formats: PDF, DOC, DOCX, JPG, PNG
   - Max Size: 5 MB
   - Required: Yes

2. **Coach Recommendation**
   - Type: Letter of Recommendation
   - Description: "Must be from your current coach or athletic director"
   - Formats: PDF, DOC, DOCX
   - Max Size: 5 MB
   - Required: Yes

### Scenario 3: Research Scholarship
**New Requirements Added:**
1. **Research Proposal**
   - Type: Other Document
   - Custom Name: "Research Proposal"
   - Description: "5-10 page proposal including methodology and expected outcomes"
   - Formats: PDF, DOC, DOCX
   - Max Size: 10 MB
   - Required: Yes

2. **Faculty Endorsement**
   - Type: Letter of Recommendation
   - Description: "From a faculty member in your field of study"
   - Formats: PDF
   - Max Size: 5 MB
   - Required: Yes

## Tips and Best Practices

### ✅ Do's:
- **Be specific** in descriptions to help students understand what's needed
- **Set appropriate file size limits** based on document type (larger for portfolios, smaller for letters)
- **Use "Other Document"** for scholarship-specific requirements
- **Test the form** before publishing the scholarship

### ❌ Don'ts:
- **Don't make everything required** if some documents are optional
- **Don't set file sizes too small** (students may have trouble compressing files)
- **Don't forget to fill in custom names** when using "Other Document" type
- **Don't add duplicate requirements** - check existing requirements first

## Troubleshooting

### Issue: Custom name field not appearing
**Solution**: Make sure you selected "Other Document" from the Document Type dropdown

### Issue: Can't remove a requirement
**Solution**: Click the X button in the top-right corner of the requirement card

### Issue: Form won't submit
**Solution**: Check that all required fields are filled:
- Document Type must be selected
- Custom Name must be filled if "Other" is selected
- File formats must be specified
- Max file size must be between 1-50

### Issue: Requirements not saving
**Solution**: Ensure you're clicking the "Create Scholarship" button at the bottom of the form, not just the "Add New Requirement" button

## Technical Notes

### For Developers:
- Dynamic requirements are created as `DocumentRequirement` objects in the database
- They become available for reuse in other scholarships
- Field names follow the pattern: `new_doc_[field]_[counter]`
- JavaScript handles the UI, Django handles the backend processing
- Requirements are only created when the scholarship form is successfully submitted

### Database Impact:
- Each new requirement creates a row in the `DocumentRequirement` table
- Requirements are linked to scholarships via a many-to-many relationship
- Requirements can be shared across multiple scholarships
- Deleting a scholarship doesn't delete the requirements (they remain available)

## Support

If you encounter any issues or have questions about this feature, please contact the development team or refer to the main documentation.
