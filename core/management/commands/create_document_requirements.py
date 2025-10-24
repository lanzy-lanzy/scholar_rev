from django.core.management.base import BaseCommand
from core.models import DocumentRequirement


class Command(BaseCommand):
    help = 'Create default document requirements for scholarships'

    def handle(self, *args, **options):
        # Default document requirements
        default_requirements = [
            {
                'name': 'certificate_enrollment',
                'description': 'Official certificate of enrollment from the registrar',
                'is_required': True,
                'file_format_requirements': 'PDF, JPG, PNG',
                'max_file_size_mb': 5
            },
            {
                'name': 'certificate_grades',
                'description': 'Official certificate of grades or transcript',
                'is_required': True,
                'file_format_requirements': 'PDF, JPG, PNG',
                'max_file_size_mb': 5
            },
            {
                'name': 'certificate_indigency',
                'description': 'Certificate of indigency from barangay or local government',
                'is_required': False,
                'file_format_requirements': 'PDF, JPG, PNG',
                'max_file_size_mb': 5
            },
            {
                'name': 'birth_certificate',
                'description': 'PSA birth certificate',
                'is_required': False,
                'file_format_requirements': 'PDF, JPG, PNG',
                'max_file_size_mb': 5
            },
            {
                'name': 'barangay_clearance',
                'description': 'Barangay clearance',
                'is_required': False,
                'file_format_requirements': 'PDF, JPG, PNG',
                'max_file_size_mb': 5
            },
            {
                'name': 'recommendation_letter',
                'description': 'Letter of recommendation from faculty or employer',
                'is_required': False,
                'file_format_requirements': 'PDF, DOC, DOCX',
                'max_file_size_mb': 5
            },
            {
                'name': 'essay',
                'description': 'Personal essay or statement of purpose',
                'is_required': False,
                'file_format_requirements': 'PDF, DOC, DOCX',
                'max_file_size_mb': 5
            },
            {
                'name': 'transcript',
                'description': 'Official academic transcript',
                'is_required': False,
                'file_format_requirements': 'PDF, JPG, PNG',
                'max_file_size_mb': 5
            },
            {
                'name': 'tax_return',
                'description': 'Income tax return (ITR) or certificate of no income',
                'is_required': False,
                'file_format_requirements': 'PDF, JPG, PNG',
                'max_file_size_mb': 5
            },
            {
                'name': 'payslip',
                'description': 'Recent payslip or income certificate',
                'is_required': False,
                'file_format_requirements': 'PDF, JPG, PNG',
                'max_file_size_mb': 5
            }
        ]

        created_count = 0
        for req_data in default_requirements:
            requirement, created = DocumentRequirement.objects.get_or_create(
                name=req_data['name'],
                defaults=req_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created document requirement: {requirement.get_name_display()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Document requirement already exists: {requirement.get_name_display()}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new document requirements')
        )