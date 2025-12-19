# SmartKeja Django Architecture

## Overview
This document outlines the Django architecture for SmartKeja, a unified PropTech platform for Kenya & Africa.

## Project Structure

```
smartkeja/
├── accounts/          # User account management
├── roles/             # Multi-role system & role switching
├── kyc/               # KYC verification (ID, KRA PIN, Face Match, Title Deed)
├── locations/         # Location hierarchy (County → Sub-County → Ward → Estate)
├── properties/        # Property listings (Rentals, Airbnb, Commercial, Land, Sales)
├── payments/          # Payment processing (M-Pesa STK Push, etc.)
├── wallet/            # User wallets, transactions, credit scores
├── bookings/          # Viewing bookings & Airbnb reservations (to be created)
├── maintenance/       # Maintenance & repairs (to be created)
├── reviews/           # Reviews, ratings & trust scores (to be created)
├── leases/            # Digital leases & e-signatures (to be created)
├── sales/             # Property sales marketplace (to be created)
├── mortgage/          # Mortgage marketplace (to be created)
├── analytics/         # Analytics & insights (to be created)
├── antiscam/          # Anti-scam AI & fraud detection (to be created)
├── compliance/        # County compliance tracking (to be created)
└── communication/     # Notifications & SMS (to be created)
```

## Core Apps Implemented

### 1. Roles App (`roles/`)
**Purpose**: Multi-role user system allowing users to switch between roles without re-registering.

**Models**:
- `UserRole`: Stores user roles (Tenant, Landlord, Agent, Caretaker, Airbnb Host/Guest, Buyer/Seller, Developer, Lawyer, Admin)
- `RoleSession`: Tracks current active role for user sessions

**Middleware**:
- `RoleSwitchingMiddleware`: Manages role switching and provides `request.current_role` to views

**Key Features**:
- Users can have multiple roles simultaneously
- Role switching without re-registration
- Primary role designation
- Role-specific metadata storage

### 2. KYC App (`kyc/`)
**Purpose**: Know Your Customer verification system for fraud prevention.

**Models**:
- `KYCVerification`: Main KYC record with ID, KRA PIN, face match, title deed verification
- `VerificationBadge`: Verification badges displayed on profiles

**Verification Levels**:
- Basic: ID only
- Standard: ID + KRA PIN
- Advanced: ID + KRA PIN + Face Match
- Premium: All + Title Deed (for landlords/sellers)

**Key Features**:
- Document upload and verification
- AI/ML fraud risk scoring
- Verification badges
- Expiry tracking

### 3. Locations App (`locations/`)
**Purpose**: Kenya-specific location hierarchy and GPS intelligence.

**Models**:
- `County`: Kenya's 47 counties
- `SubCounty`: Sub-counties within counties
- `Ward`: Wards within sub-counties
- `Estate`: Estates/areas within wards
- `LocationPin`: GPS pins for specific locations

**Key Features**:
- Complete Kenya location hierarchy
- GPS coordinate validation (Kenya bounds)
- Popular area tagging
- Property count caching

### 4. Properties App (`properties/`)
**Purpose**: Unified property listings supporting multiple property types.

**Enhanced Models**:
- `Property`: Expanded to support:
  - **Listing Types**: Rental, Airbnb, Commercial, Land, Sale
  - **Property Types**: Apartment, House, Studio, Bedsitter, Townhouse, Villa, Penthouse, Commercial Building, Office Space, Shop, Warehouse, Plot, Farm
  - Integration with new location system
  - Multi-unit building support
  - Airbnb-specific fields (nightly rate, cleaning fee, minimum nights)
  - Agent/Caretaker assignment
  - Featured listings & "Best Value" tagging

**Key Features**:
- Minimum media requirements (5 photos + video)
- GPS stamping and watermarking
- Verification workflow
- Multi-unit building support

### 5. Payments App (`payments/`)
**Purpose**: Payment processing and payouts.

**Models**:
- `Payment`: Payment records for various payment types
- `Payout`: Payouts to landlords, hosts, agents

**Payment Types**:
- Rent payments
- Deposits
- Booking payments
- Airbnb bookings
- Maintenance fees
- Subscriptions
- Featured listings
- Commissions

**Payment Methods**:
- M-Pesa STK Push
- M-Pesa Paybill
- Bank Transfer
- Card
- Wallet

**Key Features**:
- M-Pesa STK Push integration ready
- Partial payment support
- Automated receipt generation
- Platform and transaction fees

### 6. Wallet App (`wallet/`)
**Purpose**: User wallets, transactions, and credit scores.

**Models**:
- `Wallet`: User wallet with balance and credit score
- `Transaction`: Transaction records
- `PaymentStatement`: PDF statements

**Key Features**:
- Wallet balance management
- Credit score tracking (0-1000)
- Transaction history
- PDF statement generation
- M-Pesa receipt tracking

## Database Schema Highlights

### User Roles Flow
```
User → UserRole (multiple) → RoleSession (current active)
```

### KYC Flow
```
User + RoleType → KYCVerification → VerificationBadge
```

### Location Hierarchy
```
County → SubCounty → Ward → Estate → LocationPin
```

### Property Flow
```
User (owner) → Property → Estate → LocationPin
Property → PropertyImage (min 5)
Property → PropertyVideo (verification video)
Property → PropertyAmenity
```

### Payment Flow
```
User → Payment → Wallet → Transaction
User → Payout
```

## Middleware Stack

1. SecurityMiddleware
2. SessionMiddleware
3. CommonMiddleware
4. CsrfViewMiddleware
5. AuthenticationMiddleware
6. **RoleSwitchingMiddleware** (custom) - Manages role switching
7. MessageMiddleware
8. XFrameOptionsMiddleware

## Settings Configuration

### Installed Apps
- `accounts`
- `roles`
- `kyc`
- `locations`
- `properties`
- `payments`
- `wallet`

### Key Settings
- `TIME_ZONE = 'Africa/Nairobi'`
- `LANGUAGE_CODE = 'en-us'`
- Media and static files configured

## Next Steps (To Be Implemented)

### Phase 1 - MVP (Fast Revenue)
- [x] Multi-role user system
- [x] KYC verification
- [x] Location hierarchy
- [x] Enhanced property model
- [x] Payment & wallet system
- [ ] Bookings app (viewings, Airbnb reservations)
- [ ] Search & map explorer
- [ ] Viewing & booking system

### Phase 2 - Operations
- [ ] Maintenance app (repairs, caretaker operations)
- [ ] Reviews & ratings system
- [ ] Digital leases & e-signatures
- [ ] Communication hub (notifications, SMS)

### Phase 3 - Security & Analytics
- [ ] Anti-scam AI (duplicate image detection, fraud scoring)
- [ ] Analytics & insights (heatmaps, price prediction)
- [ ] Compliance tracking (fire certificates, Airbnb licenses)

### Phase 4 - High Revenue
- [ ] Property sales marketplace
- [ ] Mortgage marketplace (bank comparisons, prequalification)

## API Endpoints (To Be Created)

### Authentication & Roles
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - Login
- `POST /api/roles/switch/` - Switch active role
- `GET /api/roles/list/` - List user roles

### KYC
- `POST /api/kyc/submit/` - Submit KYC documents
- `GET /api/kyc/status/` - Get KYC status
- `POST /api/kyc/upload-document/` - Upload document

### Properties
- `GET /api/properties/` - List properties (with filters)
- `POST /api/properties/` - Create property listing
- `GET /api/properties/{id}/` - Property details
- `POST /api/properties/{id}/verify/` - Verify property

### Payments
- `POST /api/payments/mpesa/stk-push/` - Initiate M-Pesa STK Push
- `POST /api/payments/mpesa/callback/` - M-Pesa callback
- `GET /api/payments/history/` - Payment history

### Wallet
- `GET /api/wallet/balance/` - Get wallet balance
- `POST /api/wallet/deposit/` - Deposit funds
- `GET /api/wallet/transactions/` - Transaction history
- `GET /api/wallet/statement/` - Generate statement

## Security Considerations

1. **KYC Verification**: All landlords, agents, and sellers must complete KYC
2. **Role-Based Access**: Middleware enforces role-based permissions
3. **GPS Validation**: All coordinates validated against Kenya bounds
4. **Media Requirements**: Minimum 5 photos + video for verified listings
5. **Fraud Detection**: AI/ML scoring for duplicate images and fraud risk
6. **Payment Security**: M-Pesa integration with secure callback handling

## Revenue Model Integration

The system is designed to support:
- Rental subscriptions
- M-Pesa transaction fees
- Airbnb booking commission
- Featured listings
- Property sales commission (1-3%)
- Mortgage referral commission
- Document processing fees

## Development Notes

- All models include proper indexes for performance
- Foreign keys use `related_name` for reverse lookups
- Decimal fields used for currency (KES)
- Timestamps (`created_at`, `updated_at`) on all models
- Status fields use choices for data integrity
- JSON fields for flexible metadata storage

## Migration Strategy

1. Run migrations for new apps:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

3. Load initial data (Kenya counties, sub-counties, etc.)

4. Test role switching and KYC workflows

## Future Enhancements

- Redis caching for location data
- Celery for background tasks (KYC processing, statement generation)
- Elasticsearch for property search
- Real-time notifications (WebSockets)
- Mobile app API (Django REST Framework)
- AI/ML services for image verification and fraud detection

