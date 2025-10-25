"""
Migration script to add campus field to UserProfile model.
Run this script to create and apply the migration.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scholar_.settings')
django.setup()

from django.core.management import call_command

def create_and_apply_migration():
    """Create and apply migration for campus field."""
    print("Creating migration for campus field...")
    
    try:
        # Create migration
        call_command('makemigrations', 'core', verbosity=2)
        print("\n✓ Migration created successfully!")
        
        # Apply migration
        print("\nApplying migration...")
        call_command('migrate', verbosity=2)
        print("\n✓ Migration applied successfully!")
        
        print("\n" + "="*60)
        print("Campus field has been added to UserProfile model!")
        print("Students can now select from:")
        print("  - Dumingag Campus")
        print("  - Mati Campus")
        print("  - Canuto Campus")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_and_apply_migration()
