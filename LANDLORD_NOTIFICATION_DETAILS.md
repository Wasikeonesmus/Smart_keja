# Landlord Notification - Complete Details

## What the Landlord Receives via WhatsApp

When a tenant books a viewing, the landlord automatically receives a comprehensive WhatsApp message with:

### 1. **Guest Details**
- Guest name
- Email address
- Phone number
- WhatsApp updates preference (enabled/disabled)

### 2. **Property Information**
- Property name
- Listing type (Rental, Airbnb, Commercial, Land, Sale)
- Property type (Apartment, House, Studio, etc.)
- Full location address
- Number of bedrooms
- Number of bathrooms
- Property size (square meters / square feet)
- Property description (shortened)

### 3. **Payment Information**
- Monthly rent/price
- Security deposit amount
- Currency (KES)

### 4. **Location & Map**
- **Google Maps Link**: Direct link to view property on map
- **Directions Link**: Get directions to the property
- Both links use the property's GPS coordinates (latitude/longitude)

### 5. **Viewing Schedule**
- Viewing date (formatted)
- Viewing time slot
- Instructions to confirm or reschedule

### 6. **Admin Link**
- Direct link to manage the booking in admin panel

## Example Message Format

```
🏠 New Booking Request - SmartKeja

Hello Landlord Name,

Someone wants to view your property!

━━━━━━━━━━━━━━━━━━━━
📋 GUEST DETAILS
━━━━━━━━━━━━━━━━━━━━
👤 Name: John Doe
📧 Email: john@example.com
📱 Phone: 0712345678
✅ WhatsApp Updates Enabled

━━━━━━━━━━━━━━━━━━━━
🏘️ PROPERTY INFORMATION
━━━━━━━━━━━━━━━━━━━━
🏠 Property: Modern 2BR Apartment
📋 Listing: Rental
🏗️ Type: Apartment
📍 Location: Kilimani, Nairobi
🛏️ Bedrooms: 2
🚿 Bathrooms: 2
📐 Size: 85 m² (915 sq ft)
💵 Price: KES 35,000/month
💰 Deposit: KES 70,000
📝 Description: Beautiful modern apartment with balcony...

━━━━━━━━━━━━━━━━━━━━
🗺️ LOCATION & DIRECTIONS
━━━━━━━━━━━━━━━━━━━━
📍 View on Map:
https://www.google.com/maps?q=-1.2921,36.8219

🧭 Get Directions:
https://www.google.com/maps/dir/?api=1&destination=-1.2921,36.8219

━━━━━━━━━━━━━━━━━━━━
📅 VIEWING SCHEDULE
━━━━━━━━━━━━━━━━━━━━
📅 Date: Friday, December 20, 2025
⏰ Time: 10:00 AM

Please confirm availability or contact the guest to reschedule.

🔗 Manage Booking:
https://smartkeja.com/admin/properties/booking/123/change/
```

## Features Included

✅ **Property Name** - Full property name
✅ **Location** - Complete address
✅ **Map Link** - Google Maps view of property
✅ **Directions** - Get directions to property
✅ **Property Details** - Bedrooms, bathrooms, size
✅ **Payment Info** - Rent and deposit amounts
✅ **Guest Contact** - Name, email, phone
✅ **Viewing Schedule** - Date and time
✅ **Admin Link** - Manage booking directly

## Map & Directions

The notification includes:
- **Google Maps Link**: Opens property location in Google Maps
- **Directions Link**: Provides turn-by-turn directions to the property

Both links use the property's GPS coordinates (latitude/longitude) stored in the database.

## Payment Information

Shows:
- Monthly rent/price
- Security deposit (if applicable)
- Currency (KES)

## Notes

- All information is automatically pulled from the database
- Map links only appear if property has GPS coordinates
- Description is shortened to 150 characters for WhatsApp
- Landlord receives notification immediately when booking is created
- Notification is sent to landlord's phone from their LandlordApplication

