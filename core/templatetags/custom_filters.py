from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary or form by key."""
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    elif hasattr(dictionary, '__getitem__'):
        try:
            return dictionary[key]
        except (KeyError, IndexError):
            return None
    return None

@register.filter
def add_class(field, css_class):
    """Add CSS class to form field."""
    return field.as_widget(attrs={'class': css_class})

@register.filter
def field_type(field):
    """Get the type of a form field."""
    return field.field.widget.__class__.__name__

@register.filter
def is_required(field):
    """Check if a form field is required."""
    return field.field.required

@register.filter
def document_field_name(requirement_id):
    """Generate document field name from requirement ID."""
    return f'document_{requirement_id}'