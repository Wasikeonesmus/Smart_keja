from django.core.management.base import BaseCommand
from properties.models import LandlordApplication
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Approve landlord applications (for testing/demo purposes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the user to approve',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Approve all pending applications',
        )

    def handle(self, *args, **options):
        if options['all']:
            applications = LandlordApplication.objects.filter(status='pending')
            count = applications.update(status='approved', review_notes='Auto-approved for testing')
            self.stdout.write(
                self.style.SUCCESS(f'Successfully approved {count} landlord application(s)')
            )
        elif options['username']:
            try:
                user = User.objects.get(username=options['username'])
                try:
                    application = LandlordApplication.objects.get(user=user, status='pending')
                    application.status = 'approved'
                    application.review_notes = 'Auto-approved for testing'
                    application.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully approved application for {user.username}')
                    )
                except LandlordApplication.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'No pending application found for user {options["username"]}')
                    )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User {options["username"]} not found')
                )
        else:
            # Approve the most recent pending application
            try:
                application = LandlordApplication.objects.filter(status='pending').order_by('-created_at').first()
                if application:
                    application.status = 'approved'
                    application.review_notes = 'Auto-approved for testing'
                    application.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully approved application for {application.user.username}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('No pending applications found')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error: {str(e)}')
                )

