# SmartKeja Quick Start Guide

## What Has Been Built

I've created the foundational architecture for SmartKeja with the following core components:

### ✅ Completed Components

1. **Multi-Role User System** (`roles/`)
   - Users can have multiple roles (Tenant, Landlord, Agent, Caretaker, Airbnb Host/Guest, Buyer/Seller, Developer, Lawyer, Admin)
   - Role switching middleware
   - Role session management

2. **KYC Verification System** (`kyc/`)
   - ID verification
   - KRA PIN verification
   - Face matching
   - Title deed verification
   - Verification badges

3. **Location Intelligence** (`locations/`)
   - Complete Kenya location hierarchy (County → Sub-County → Ward → Estate)
   - GPS pinning system
   - Location validation

4. **Enhanced Property Model** (`properties/`)
   - Supports Rentals, Airbnb, Commercial, Land, and Sales
   - Multiple property types (Apartment, House, Studio, Bedsitter, etc.)
   - Multi-unit building support
   - Integration with new location system

5. **Payment System** (`payments/`)
   - M-Pesa STK Push ready
   - Multiple payment types
   - Payout system

6. **Wallet System** (`wallet/`)
   - User wallets with balance
   - Credit score tracking
   - Transaction history
   - PDF statement generation

## Next Steps

### 1. Run Migrations

```bash
cd "c:\Users\user\Desktop\Djang App"
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

### 3. Test the System

1. **Access Django Admin**: `http://127.0.0.1:8000/admin/`
2. **Create a User Role**: Go to Roles → User Roles → Add
3. **Test KYC**: Go to KYC → KYC Verifications → Add
4. **Add Locations**: Go to Locations → Counties → Add (start with Nairobi)

### 4. Load Initial Location Data

You can create a management command or use Django admin to populate Kenya's 47 counties and sub-counties. The location data structure is ready in `locations/models.py`.

### 5. Update Requirements

Add these to `requirements.txt` if needed:
```
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.2.0
celery>=5.3.0
redis>=5.0.0
Pillow>=10.0.0
```

## Key Files Created

### Models
- `roles/models.py` - Multi-role system
- `kyc/models.py` - KYC verification
- `locations/models.py` - Location hierarchy
- `wallet/models.py` - Wallet system
- `payments/models.py` - Payment processing
- `properties/models.py` - Enhanced property model

### Middleware
- `roles/middleware.py` - Role switching middleware

### Admin
- All apps have admin configurations for easy management

### Documentation
- `SMARTKEJA_ARCHITECTURE.md` - Complete architecture documentation

## Important Notes

1. **Role Switching**: The middleware automatically sets `request.current_role` for authenticated users
2. **Location System**: Properties can use the new `Estate` model or legacy fields (backward compatible)
3. **KYC**: Each user role can have separate KYC verification
4. **Payments**: M-Pesa STK Push integration structure is ready, needs API credentials
5. **Wallet**: Automatically created when user registers (you may want to add a signal)

## Testing Role Switching

After creating a user and assigning roles:

```python
# In Django shell or view
from roles.models import UserRole, RoleSession
from django.contrib.auth.models import User

user = User.objects.first()
# Add roles
UserRole.add_role(user, 'tenant', is_primary=True)
UserRole.add_role(user, 'landlord', is_primary=False)

# Switch role (in a view)
role_session = RoleSession.objects.get(user=user)
new_role = UserRole.objects.get(user=user, role_type='landlord')
role_session.current_role = new_role
role_session.save()
```

## Next Phase: Bookings & Viewings

The next logical step is to create the `bookings` app for:
- Property viewing appointments
- Airbnb reservations
- Calendar management
- Virtual viewing support

## Questions?

Refer to `SMARTKEJA_ARCHITECTURE.md` for detailed architecture documentation.

