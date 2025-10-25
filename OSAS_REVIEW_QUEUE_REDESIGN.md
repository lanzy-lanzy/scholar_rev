# OSAS Review Queue - Modern Redesign

## Overview
Complete redesign of the OSAS review queue with modern table view, improved cards, and better pagination.

## Key Features

### 1. Dual View Mode
- **Table View**: Clean, sortable table with all information at a glance
- **Card View**: Visual cards with more details and better mobile support
- **Toggle**: Easy switch between views with saved preference

### 2. Modern Table Design
```
┌────────────────────────────────────────────────────────────────┐
│ Student Name  │ Scholarship    │ GPA  │ Date      │ Status    │
├────────────────────────────────────────────────────────────────┤
│ John Doe      │ Academic Ex... │ 3.85 │ Oct 25    │ ⚪ Pending │
│ Jane Smith    │ Innovation ... │ 3.92 │ Oct 24    │ 🔵 Review │
│ Bob Johnson   │ Merit Award    │ 3.78 │ Oct 23    │ ⚪ Pending │
└────────────────────────────────────────────────────────────────┘
```

### 3. Enhanced Filters
- Status tabs with counts
- Scholarship dropdown
- Priority filter
- Search by student name
- Date range filter

### 4. Better Pagination
- Page numbers
- Previous/Next buttons
- Results count
- Jump to page
- Items per page selector

### 5. Quick Actions
- Bulk select
- Bulk assign
- Export to CSV
- Print view
- Refresh button

## Implementation

### Step 1: Add Table View HTML

Add this after the card view section in `templates/osas/review_queue.html`:

```html
<!-- Table View -->
<div id="tableView" style="display: none;">
    <div class="modern-table-container">
        <table class="modern-table">
            <thead>
                <tr>
                    <th>
                        <input type="checkbox" id="selectAll" class="rounded">
                    </th>
                    <th>Student</th>
                    <th>Scholarship</th>
                    <th>GPA</th>
                    <th>Submitted</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for application in applications %}
                <tr>
                    <td>
                        <input type="checkbox" class="app-checkbox rounded" value="{{ application.id }}">
                    </td>
                    <td>
                        <div class="flex items-center">
                            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center text-white font-bold mr-3">
                                {{ application.student.first_name.0 }}{{ application.student.last_name.0 }}
                            </div>
                            <div>
                                <div class="font-semibold text-gray-900">
                                    {{ application.student.get_full_name }}
                                </div>
                                <div class="text-xs text-gray-500">
                                    {{ application.student.email }}
                                </div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="font-medium text-gray-900">
                            {{ application.scholarship.title|truncatewords:5 }}
                        </div>
                        <div class="text-xs text-gray-500">
                            ${{ application.scholarship.award_amount|floatformat:0 }}
                        </div>
                    </td>
                    <td>
                        <span class="font-semibold text-cyan-600">
                            {{ application.gpa }}
                        </span>
                    </td>
                    <td>
                        <div class="text-sm text-gray-900">
                            {{ application.submitted_at|date:"M d, Y" }}
                        </div>
                        <div class="text-xs text-gray-500">
                            {{ application.submitted_at|timesince }} ago
                        </div>
                    </td>
                    <td>
                        {% if application.status == 'pending' %}
                            <span class="status-badge badge-pending">Pending</span>
                        {% elif application.status == 'under_review' %}
                            <span class="status-badge badge-under-review">Under Review</span>
                        {% endif %}
                    </td>
                    <td>
                        <div class="flex gap-2">
                            {% if application.status == 'pending' %}
                                <form method="POST" action="{% url 'core:assign_application' application.id %}" class="inline">
                                    {% csrf_token %}
                                    <button type="submit" class="btn-success btn-xs">
                                        Assign
                                    </button>
                                </form>
                            {% endif %}
                            <a href="{% url 'core:review_application' application.id %}" 
                               class="btn-secondary btn-xs">
                                Review
                            </a>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
```

### Step 2: Update View Toggle

Replace the view toggle section with:

```html
<div class="flex items-center gap-4">
    <!-- View Toggle -->
    <div class="view-toggle">
        <button type="button" class="view-toggle-btn active" id="cardViewBtn" onclick="switchView('card')">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
            </svg>
            Cards
        </button>
        <button type="button" class="view-toggle-btn" id="tableViewBtn" onclick="switchView('table')">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
            </svg>
            Table
        </button>
        <button type="button" class="view-toggle-btn" id="listViewBtn" onclick="switchView('list')">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
            List
        </button>
    </div>
    
    <!-- Bulk Actions -->
    <div class="flex gap-2">
        <button type="button" onclick="bulkAssign()" class="btn-outline btn-sm">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            Bulk Assign
        </button>
        <button type="button" onclick="exportToCSV()" class="btn-outline btn-sm">
            <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Export
        </button>
    </div>
</div>
```

### Step 3: Update JavaScript

Replace the switchView function with:

```javascript
function switchView(viewType) {
    const cardView = document.getElementById('cardView');
    const listView = document.getElementById('listView');
    const tableView = document.getElementById('tableView');
    const cardBtn = document.getElementById('cardViewBtn');
    const listBtn = document.getElementById('listViewBtn');
    const tableBtn = document.getElementById('tableViewBtn');
    
    // Hide all views
    if (cardView) cardView.style.display = 'none';
    if (listView) listView.style.display = 'none';
    if (tableView) tableView.style.display = 'none';
    
    // Remove active class from all buttons
    if (cardBtn) cardBtn.classList.remove('active');
    if (listBtn) listBtn.classList.remove('active');
    if (tableBtn) tableBtn.classList.remove('active');
    
    // Show selected view and activate button
    if (viewType === 'card') {
        if (cardView) cardView.style.display = 'block';
        if (cardBtn) cardBtn.classList.add('active');
    } else if (viewType === 'table') {
        if (tableView) tableView.style.display = 'block';
        if (tableBtn) tableBtn.classList.add('active');
    } else {
        if (listView) listView.style.display = 'block';
        if (listBtn) listBtn.classList.add('active');
    }
    
    localStorage.setItem('reviewQueueView', viewType);
}

// Select all checkboxes
document.getElementById('selectAll')?.addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.app-checkbox');
    checkboxes.forEach(cb => cb.checked = this.checked);
});

// Bulk assign function
function bulkAssign() {
    const selected = Array.from(document.querySelectorAll('.app-checkbox:checked'))
        .map(cb => cb.value);
    
    if (selected.length === 0) {
        alert('Please select at least one application');
        return;
    }
    
    if (confirm(`Assign ${selected.length} application(s) to yourself?`)) {
        // Submit form or make AJAX request
        console.log('Assigning applications:', selected);
        // TODO: Implement bulk assign logic
    }
}

// Export to CSV function
function exportToCSV() {
    const table = document.querySelector('.modern-table');
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => col.textContent.trim());
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'applications.csv';
    a.click();
}

// Load saved view preference
document.addEventListener('DOMContentLoaded', function() {
    const savedView = localStorage.getItem('reviewQueueView') || 'card';
    switchView(savedView);
});
```

### Step 4: Add CSS for Table

Add these styles to the `<style>` section:

```css
.modern-table-container {
    overflow-x: auto;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.modern-table {
    width: 100%;
    background: white;
    border-collapse: separate;
    border-spacing: 0;
}

.modern-table thead {
    background: linear-gradient(135deg, #0e7490 0%, #0891b2 100%);
    color: white;
}

.modern-table th {
    padding: 1rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.modern-table tbody tr {
    border-bottom: 1px solid #e5e7eb;
    transition: all 0.2s;
}

.modern-table tbody tr:last-child {
    border-bottom: none;
}

.modern-table tbody tr:hover {
    background: #f9fafb;
}

.modern-table td {
    padding: 1rem;
    font-size: 0.875rem;
    vertical-align: middle;
}

/* Responsive table */
@media (max-width: 768px) {
    .modern-table {
        font-size: 0.75rem;
    }
    
    .modern-table th,
    .modern-table td {
        padding: 0.5rem;
    }
}
```

## Benefits

### 1. Better Data Density
- Table view shows more applications at once
- Easier to scan and compare
- Better for desktop users

### 2. Improved Usability
- Bulk actions save time
- Export functionality for reports
- Sortable columns (can be added)
- Filterable data

### 3. Modern Design
- Clean, professional look
- Consistent with updated button styles
- Better contrast and readability
- Smooth animations

### 4. Mobile Responsive
- Cards work better on mobile
- Table scrolls horizontally
- List view for medium screens

## Testing Checklist

- [ ] Table view displays correctly
- [ ] Card view still works
- [ ] List view still works
- [ ] View toggle saves preference
- [ ] Checkboxes work
- [ ] Select all works
- [ ] Bulk assign works
- [ ] Export to CSV works
- [ ] Pagination works in all views
- [ ] Filters work in all views
- [ ] Mobile responsive
- [ ] No JavaScript errors

## Future Enhancements

1. **Sortable Columns**: Click column headers to sort
2. **Advanced Filters**: Date range, GPA range, etc.
3. **Saved Filters**: Save common filter combinations
4. **Bulk Actions**: Bulk review, bulk reject, etc.
5. **Keyboard Shortcuts**: Navigate with keyboard
6. **Real-time Updates**: Auto-refresh new applications
7. **Column Customization**: Show/hide columns
8. **Density Options**: Compact, comfortable, spacious

---

**Status**: Ready to Implement
**Estimated Time**: 2-3 hours
**Difficulty**: Medium
