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
from django.http import HttpRequest
from django.contrib.auth.models import User, AnonymousUser

try:
    template = get_template('landing.html')
    print("Landing template loaded successfully!")
    
    # Create a mock request object
    request = HttpRequest()
    request.path = '/'
    request.user = AnonymousUser()
    
    # Try to render with a landing page context
    context = {
        'user': AnonymousUser(),
        'messages': [],
        'request': request,
        'total_scholarships': 50,
        'total_applications': 1000,
    }
    rendered = template.render(context)
    print(f"Landing template rendered successfully! Length: {len(rendered)} characters")
    
except TemplateSyntaxError as e:
    print(f"Template Syntax Error: {e}")
    print(f"Template: {e.template_debug.get('name', 'Unknown')}")
    print(f"Line: {e.template_debug.get('line', 'Unknown')}")
    print(f"During: {e.template_debug.get('during', 'Unknown')}")
    
    if 'source' in e.template_debug and e.template_debug['source']:
        lines = e.template_debug['source']
        error_line = e.template_debug.get('line', 0)
        
        # Show lines around the error
        start = max(0, error_line - 5)
        end = min(len(lines), error_line + 5)
        
        print(f"\nTemplate content around line {error_line}:")
        for i in range(start, end):
            line_num = i + 1
            marker = " -> " if line_num == error_line else "    "
            print(f"{marker}{line_num:3d}: {lines[i]}")
            
except Exception as e:
    print(f"Other error: {e}")
    import traceback
    traceback.print_exc()