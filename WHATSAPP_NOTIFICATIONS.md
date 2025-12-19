# WhatsApp Notification System

## How WhatsApp Messages Work

### When a Tenant Books a Property:

#### 1. **Tenant WhatsApp Confirmation** (if enabled)
- **Sent to:** Tenant's phone number (the one they entered in the booking form)
- **When:** Immediately after booking is confirmed
- **Content:** Booking confirmation with property details, date, and time
- **Only if:** Tenant checked "Send me WhatsApp updates"

**Example:**
```
🏠 SmartKeja Booking Confirmation

Hello John Doe,

Your property viewing has been confirmed!

📅 Date: Friday, December 20, 2025
⏰ Time: 10:00 AM
🏘️ Property: Modern 2BR Apartment

We'll send you a reminder 24 hours before your viewing.

Thank you for choosing SmartKeja!
```

#### 2. **Landlord WhatsApp Notification** (automatic)
- **Sent to:** Landlord's phone number (from their LandlordApplication)
- **When:** Immediately after booking is created
- **Content:** New booking request with guest details
- **Always sent:** Yes, landlord is always notified

**Example:**
```
🏠 New Booking Request - SmartKeja

Hello Landlord Name,

Someone wants to view your property!

📋 Guest Details:
👤 Name: John Doe
📧 Email: john@example.com
📱 Phone: 0712345678

🏘️ Property: Modern 2BR Apartment
📍 Location: Kilimani, Nairobi

📅 Viewing Date: Friday, December 20, 2025
⏰ Time: 10:00 AM

Please confirm availability or contact the guest to reschedule.

View booking: [admin link]
```

## Summary

| Who | WhatsApp Sent To | When | Required? |
|-----|-----------------|------|-----------|
| **Tenant** | Tenant's phone number | After booking | Only if tenant enables it |
| **Landlord** | Landlord's phone number | After booking | Always (automatic) |

## How It Works

1. **Tenant books property** → Enters their phone number
2. **If WhatsApp enabled** → Tenant gets confirmation message to their WhatsApp
3. **Landlord automatically notified** → Gets notification to their WhatsApp (from LandlordApplication)

## Phone Number Sources

- **Tenant WhatsApp:** From booking form (`booking.phone`)
- **Landlord WhatsApp:** From LandlordApplication (`landlord.landlord_application.phone`)

## Notes

- Landlord notification is **always sent** (automatic)
- Tenant notification is **optional** (only if they check the WhatsApp checkbox)
- Both use WhatsApp Web links (can be upgraded to WhatsApp Business API)
- Phone numbers are automatically formatted with Kenya country code (+254)

