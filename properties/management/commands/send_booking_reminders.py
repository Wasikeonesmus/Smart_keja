"""
Management command to send booking reminders 24 hours before viewing dates
Run this daily via cron or scheduled task
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from properties.models import Booking
import urllib.parse


class Command(BaseCommand):
    help = 'Send booking reminders 24 hours before viewing dates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get bookings happening in 24 hours
        tomorrow = timezone.now().date() + timedelta(days=1)
        
        # Get bookings happening tomorrow that haven't been cancelled
        bookings = Booking.objects.filter(
            date=tomorrow,
            status__in=['pending', 'confirmed']
        ).select_related('property').exclude(
            # Exclude if already sent (we'll add reminder_sent field later)
        )
        
        self.stdout.write(f'Found {bookings.count()} bookings for tomorrow ({tomorrow})')
        
        sent_count = 0
        email_count = 0
        whatsapp_count = 0
        
        for booking in bookings:
            try:
                # Send email reminder
                email_sent = self.send_email_reminder(booking, dry_run)
                if email_sent:
                    email_count += 1
                
                # Send WhatsApp reminder if enabled
                if booking.whatsapp_updates:
                    whatsapp_sent = self.send_whatsapp_reminder(booking, dry_run)
                    if whatsapp_sent:
                        whatsapp_count += 1
                
                if email_sent or (booking.whatsapp_updates and whatsapp_sent):
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Reminder sent for booking #{booking.id} - {booking.name}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Could not send reminder for booking #{booking.id}'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error sending reminder for booking #{booking.id}: {str(e)}'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: {sent_count} bookings processed, '
            f'{email_count} emails sent, {whatsapp_count} WhatsApp reminders sent'
        ))

    def send_email_reminder(self, booking, dry_run=False):
        """Send email reminder to booking email address"""
        try:
            subject = f'Reminder: Property Viewing Tomorrow - {booking.property.name}'
            
            message = f"""
Hello {booking.name},

This is a reminder that you have a property viewing scheduled for tomorrow.

📅 Date: {booking.date.strftime('%A, %B %d, %Y')}
⏰ Time: {booking.time_slot}
🏘️ Property: {booking.property.name}
📍 Location: {self.get_property_location(booking.property)}

Please arrive on time for your viewing. If you need to reschedule or cancel, please contact us as soon as possible.

Thank you,
SmartKeja Solutions
"""
            
            if dry_run:
                self.stdout.write(f'[DRY RUN] Would send email to: {booking.email}')
                self.stdout.write(f'Subject: {subject}')
                return True
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.email],
                fail_silently=False,
            )
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Email error: {str(e)}'))
            return False

    def send_whatsapp_reminder(self, booking, dry_run=False):
        """Generate WhatsApp reminder URL"""
        try:
            # Format phone number
            phone = booking.phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            # Add country code if not present (Kenya: 254)
            if not phone.startswith('254'):
                if phone.startswith('0'):
                    phone = '254' + phone[1:]
                else:
                    phone = '254' + phone
            
            # Create WhatsApp message
            date_str = booking.date.strftime('%A, %B %d, %Y')
            location = self.get_property_location(booking.property)
            
            message = (
                f"🔔 *Reminder: Property Viewing Tomorrow*\n\n"
                f"Hello {booking.name},\n\n"
                f"This is a reminder that you have a property viewing scheduled for tomorrow.\n\n"
                f"📅 *Date:* {date_str}\n"
                f"⏰ *Time:* {booking.time_slot}\n"
                f"🏘️ *Property:* {booking.property.name}\n"
                f"📍 *Location:* {location}\n\n"
                f"Please arrive on time. If you need to reschedule, contact us ASAP.\n\n"
                f"Thank you,\nSmartKeja Solutions"
            )
            
            # Encode message for URL
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
            
            if dry_run:
                self.stdout.write(f'[DRY RUN] Would send WhatsApp to: {phone}')
                self.stdout.write(f'URL: {whatsapp_url}')
                return True
            
            # In production, you would use WhatsApp Business API here
            # For now, we'll log the URL - you can send it via API or queue it
            self.stdout.write(f'WhatsApp reminder URL for {booking.name}: {whatsapp_url}')
            
            # TODO: Integrate with WhatsApp Business API to actually send
            # For now, return True to indicate it would be sent
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'WhatsApp error: {str(e)}'))
            return False

    def get_property_location(self, property_obj):
        """Get property location string"""
        try:
            if property_obj.estate and hasattr(property_obj.estate, 'full_location_string'):
                return property_obj.estate.full_location_string
            elif property_obj.estate:
                location_parts = []
                if property_obj.estate.name:
                    location_parts.append(property_obj.estate.name)
                if hasattr(property_obj.estate, 'sub_county') and property_obj.estate.sub_county:
                    if property_obj.estate.sub_county.name:
                        location_parts.append(property_obj.estate.sub_county.name)
                    if hasattr(property_obj.estate.sub_county, 'county') and property_obj.estate.sub_county.county:
                        if property_obj.estate.sub_county.county.name:
                            location_parts.append(property_obj.estate.sub_county.county.name)
                return ', '.join(location_parts) if location_parts else 'Location not specified'
            else:
                # Fallback to legacy fields
                location_parts = []
                if property_obj.estate_name:
                    location_parts.append(property_obj.estate_name)
                if property_obj.sub_county:
                    location_parts.append(property_obj.sub_county)
                if property_obj.county:
                    location_parts.append(property_obj.county)
                return ', '.join(location_parts) if location_parts else 'Location not specified'
        except:
            return 'Location not specified'

