#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')

# Setup Django
django.setup()

from django.template.loader import get_template
from django.template import Context, TemplateSyntaxError
from django.contrib.auth.models import User

try:
    template = get_template('base/base.html')
    print("Template loaded successfully!")
    
    # Try to render with a basic context
    context = {
        'user': None,
        'messages': [],
        'request': None,
    }
    rendered = template.render(context)
    print(f"Template rendered successfully! Length: {len(rendered)} characters")
    
except TemplateSyntaxError as e:
    print(f"Template Syntax Error: {e}")
    print(f"Line: {e.template_debug['line']}")
    print(f"During: {e.template_debug['during']}")
    if 'source' in e.template_debug:
        lines = e.template_debug['source']
        for i, line in enumerate(lines, 1):
            marker = " -> " if i == e.template_debug['line'] else "    "
            print(f"{marker}{i:3d}: {line}")
except Exception as e:
    print(f"Other error: {e}")