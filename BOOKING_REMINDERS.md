# Booking Reminder System

## Where Reminders Are Sent

### 1. **Email Reminders**
- **Sent to:** The email address provided when booking (`booking.email`)
- **When:** 24 hours before the viewing date
- **Content:** Includes property name, date, time, and location

### 2. **WhatsApp Reminders**
- **Sent to:** The phone number provided when booking (`booking.phone`)
- **When:** 24 hours before the viewing date
- **Only if:** User enabled WhatsApp updates (`whatsapp_updates = True`)
- **Content:** Formatted WhatsApp message with booking details

## How It Works

### Automatic Reminder System
A management command runs daily to send reminders:

```bash
python manage.py send_booking_reminders
```

### What Gets Sent

**Email Reminder:**
- Sent to: `booking.email` (e.g., user@example.com)
- Subject: "Reminder: Property Viewing Tomorrow - [Property Name]"
- Includes: Date, time, property name, location

**WhatsApp Reminder:**
- Sent to: `booking.phone` (e.g., +254712345678)
- Only if: `booking.whatsapp_updates = True`
- Format: WhatsApp Business API or WhatsApp Web link

## Setting Up Reminders

### 1. Configure Email Settings
Add to `smartkeja/settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@smartkeja.com'
```

### 2. Schedule the Command
Run daily via cron (Linux/Mac) or Task Scheduler (Windows):

**Linux/Mac (Cron):**
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /path/to/project && python manage.py send_booking_reminders
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `manage.py send_booking_reminders`
7. Start in: `C:\Users\user\Desktop\Djang App`

### 3. Test the Command
```bash
# Dry run (see what would be sent without actually sending)
python manage.py send_booking_reminders --dry-run

# Actually send reminders
python manage.py send_booking_reminders
```

## Reminder Details

### Email Reminder Includes:
- Guest name
- Viewing date (formatted)
- Viewing time
- Property name
- Property location
- Contact information

### WhatsApp Reminder Includes:
- Guest name
- Viewing date (formatted)
- Viewing time
- Property name
- Property location
- Rescheduling instructions

## Current Status

✅ **Reminder system created**
- Management command: `send_booking_reminders`
- Email reminder functionality
- WhatsApp reminder URL generation

⚠️ **To Complete:**
1. Configure email SMTP settings
2. Set up WhatsApp Business API (optional, for automated sending)
3. Schedule the command to run daily
4. Add `reminder_sent` field to Booking model (to prevent duplicates)

## Testing

To test reminders manually:
```bash
# See what would be sent
python manage.py send_booking_reminders --dry-run

# Send actual reminders
python manage.py send_booking_reminders
```

## Notes

- Reminders are sent 24 hours before the booking date
- Only pending and confirmed bookings receive reminders
- Cancelled bookings are excluded
- Email is sent to the email address provided during booking
- WhatsApp is sent only if the user enabled WhatsApp updates

