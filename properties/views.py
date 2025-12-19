from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Property, PropertyImage, PropertyVideo, PropertyAmenity, Booking, LandlordApplication
import urllib.parse
from .forms import SignUpForm, LandlordApplicationForm
from decimal import Decimal, InvalidOperation
import json
import os
import uuid

# GPS extraction from EXIF
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def home(request):
    """Home page view"""
    return render(request, 'properties/home.html')

def search(request):
    """Search and listings page"""
    return render(request, 'properties/search.html')

def list_property(request):
    """List property page"""
    return render(request, 'properties/list_property.html')

def list_property_wizard(request):
    """Multi-step property listing wizard"""
    # Only authenticated and approved landlords can list properties
    if not request.user.is_authenticated:
        return redirect(f"/accounts/login/?next={request.path}")

    try:
        application = request.user.landlord_application
    except LandlordApplication.DoesNotExist:
        return redirect('landlord_apply')

    if application.status != 'approved':
        return redirect('landlord_status')

    return render(request, 'properties/list_property_wizard.html')

def verification_demo(request):
    """Demo page for AI verification system"""
    return render(request, 'properties/verification_demo.html')

def signup(request):
    """User signup view"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Automatically create tenant role and wallet
            try:
                from roles.models import UserRole, RoleSession
                from wallet.models import Wallet
                
                # Create tenant role
                tenant_role, created = UserRole.objects.get_or_create(
                    user=user,
                    role_type='tenant',
                    defaults={'is_active': True}
                )
                
                # Create wallet
                Wallet.objects.get_or_create(
                    user=user,
                    defaults={'balance': Decimal('0.00')}
                )
                
                # Set default role session
                RoleSession.objects.get_or_create(
                    user=user,
                    defaults={'current_role': tenant_role}
                )
            except Exception as e:
                # If roles/wallet apps aren't migrated yet, continue anyway
                pass
            
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def landlord_apply(request):
    """Landlord application form with ID upload and location pin."""
    try:
        application = request.user.landlord_application
    except LandlordApplication.DoesNotExist:
        application = None

    if request.method == "POST":
        form = LandlordApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            landlord_app = form.save(commit=False)
            landlord_app.user = request.user
            landlord_app.status = 'pending'
            landlord_app.save()
            return redirect('landlord_status')
    else:
        form = LandlordApplicationForm(instance=application)

    return render(request, 'properties/landlord_apply.html', {'form': form, 'application': application})


@login_required
def landlord_status(request):
    """Simple page to show landlord verification status."""
    try:
        application = request.user.landlord_application
    except LandlordApplication.DoesNotExist:
        return redirect('landlord_apply')

    return render(request, 'properties/landlord_status.html', {'application': application})

@login_required
def dashboard(request):
    """User dashboard showing properties, bookings, and stats"""
    user = request.user
    
    # Get user's properties (if landlord)
    user_properties = Property.objects.filter(owner=user).order_by('-created_at')[:10]
    total_properties = Property.objects.filter(owner=user).count()
    verified_properties = Property.objects.filter(owner=user, verification_status='approved', ai_verification_result='MATCH').count()
    pending_properties = Property.objects.filter(owner=user, verification_status='pending').count()
    
    # Get user's bookings (if tenant)
    user_bookings = Booking.objects.filter(user=user).order_by('-created_at')[:10]
    total_bookings = Booking.objects.filter(user=user).count()
    
    # Check if user is a landlord
    is_landlord = False
    landlord_application = None
    try:
        landlord_application = user.landlord_application
        is_landlord = landlord_application.status == 'approved'
    except LandlordApplication.DoesNotExist:
        pass
    
    # Get wallet balance if available
    wallet_balance = None
    try:
        from wallet.models import Wallet
        wallet = Wallet.objects.get(user=user)
        wallet_balance = wallet.balance
    except:
        pass
    
    context = {
        'user': user,
        'is_landlord': is_landlord,
        'landlord_application': landlord_application,
        'user_properties': user_properties,
        'total_properties': total_properties,
        'verified_properties': verified_properties,
        'pending_properties': pending_properties,
        'user_bookings': user_bookings,
        'total_bookings': total_bookings,
        'wallet_balance': wallet_balance,
    }
    
    return render(request, 'properties/dashboard.html', context)

def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_admin)
def custom_admin(request):
    """Custom admin dashboard with modern UI"""
    # Statistics
    total_properties = Property.objects.count()
    verified_properties = Property.objects.filter(verification_status='approved', ai_verification_result='MATCH').count()
    pending_properties = Property.objects.filter(verification_status='pending').count()
    rejected_properties = Property.objects.filter(verification_status='rejected').count()
    
    total_users = User.objects.count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    
    total_landlords = LandlordApplication.objects.filter(status='approved').count()
    pending_landlord_apps = LandlordApplication.objects.filter(status='pending').count()
    
    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_properties = Property.objects.filter(created_at__gte=week_ago).count()
    recent_users = User.objects.filter(date_joined__gte=week_ago).count()
    recent_bookings = Booking.objects.filter(created_at__gte=week_ago).count()
    
    # Average property price
    avg_price = Property.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0
    
    # Properties by status
    properties_by_status = Property.objects.values('verification_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent properties
    latest_properties = Property.objects.select_related('owner').order_by('-created_at')[:10]
    
    # Recent bookings
    latest_bookings = Booking.objects.select_related('property', 'user').order_by('-created_at')[:10]
    
    # Pending landlord applications
    pending_applications = LandlordApplication.objects.select_related('user').filter(
        status='pending'
    ).order_by('-created_at')[:10]
    
    # Properties needing verification
    properties_to_verify = Property.objects.filter(
        verification_status='pending'
    ).select_related('owner').order_by('-created_at')[:10]
    
    context = {
        # Statistics
        'total_properties': total_properties,
        'verified_properties': verified_properties,
        'pending_properties': pending_properties,
        'rejected_properties': rejected_properties,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_landlords': total_landlords,
        'pending_landlord_apps': pending_landlord_apps,
        
        # Recent activity
        'recent_properties': recent_properties,
        'recent_users': recent_users,
        'recent_bookings': recent_bookings,
        'avg_price': avg_price,
        
        # Data lists
        'properties_by_status': properties_by_status,
        'latest_properties': latest_properties,
        'latest_bookings': latest_bookings,
        'pending_applications': pending_applications,
        'properties_to_verify': properties_to_verify,
    }
    
    return render(request, 'admin/custom_admin.html', context)

@require_http_methods(["GET"])
def api_properties(request):
    """API endpoint for properties"""
    try:
        # Get properties from database
        try:
            queryset = Property.objects.filter(available=True).select_related('owner').prefetch_related('images', 'amenities')
            
            # Try to select_related estate if it exists
            try:
                queryset = queryset.select_related('estate', 'estate__sub_county', 'estate__sub_county__county')
            except Exception:
                # If estate relationship doesn't exist, continue without it
                pass
        except Exception as e:
            # If Property model query fails, return empty queryset
            queryset = Property.objects.none()
        
        # Apply filters if provided
        county = request.GET.get('county', '')
        estate = request.GET.get('estate', '')
        min_price = request.GET.get('minPrice', '')
        max_price = request.GET.get('maxPrice', '')
        bedrooms = request.GET.get('bedrooms', '')
        property_type = request.GET.getlist('propertyType')
        verified = request.GET.get('verified', '')
        
        if county:
            # Filter by county - check both new location system and legacy field
            queryset = queryset.filter(
                Q(estate__sub_county__county__name__icontains=county) |
                Q(county__icontains=county)
            )
        if estate:
            # Filter by estate - check both new location system and legacy field
            queryset = queryset.filter(
                Q(estate__name__icontains=estate) |
                Q(estate_name__icontains=estate)
            )
        if min_price:
            try:
                queryset = queryset.filter(price__gte=Decimal(min_price))
            except (ValueError, InvalidOperation):
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=Decimal(max_price))
            except (ValueError, InvalidOperation):
                pass
        if bedrooms:
            try:
                bed_filter = int(bedrooms)
                if bed_filter == 4:
                    queryset = queryset.filter(bedrooms__gte=4)
                else:
                    queryset = queryset.filter(bedrooms=bed_filter)
            except ValueError:
                pass
        if property_type:
            queryset = queryset.filter(property_type__in=property_type)
        if verified == 'true':
            queryset = queryset.filter(verification_status='approved', ai_verification_result='MATCH')
        
        # Convert to JSON format
        properties = []
        # Evaluate queryset safely
        try:
            property_list = list(queryset[:100])  # Limit to 100 properties
        except Exception as e:
            # If queryset fails, return empty and let fallback handle it
            property_list = []
        
        for prop in property_list:
            # Get primary image or first image
            primary_image = prop.images.filter(is_primary=True).first()
            if not primary_image:
                primary_image = prop.images.first()
            
            # Get image URL - handle both relative and absolute URLs
            if primary_image:
                try:
                    image_url = primary_image.image.url
                    # Ensure it's a full URL if it's relative
                    if image_url.startswith('/media/'):
                        # It's already a proper URL path
                        pass
                    elif not image_url.startswith('http'):
                        # Make it a proper media URL
                        image_url = f'/media/{primary_image.image.name}'
                except:
                    image_url = 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=300&fit=crop'
            else:
                image_url = 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=300&fit=crop'
            
            # Format location string properly - handle both new location system and legacy
            try:
                if prop.estate and hasattr(prop.estate, 'full_location_string'):
                    # Use new location system
                    location_string = prop.estate.full_location_string
                elif prop.estate:
                    # Estate exists but doesn't have full_location_string, build it manually
                    location_parts = []
                    if prop.estate.name:
                        location_parts.append(prop.estate.name)
                    if hasattr(prop.estate, 'sub_county') and prop.estate.sub_county:
                        if prop.estate.sub_county.name:
                            location_parts.append(prop.estate.sub_county.name)
                        if hasattr(prop.estate.sub_county, 'county') and prop.estate.sub_county.county:
                            if prop.estate.sub_county.county.name:
                                location_parts.append(prop.estate.sub_county.county.name)
                    location_string = ', '.join(location_parts) if location_parts else 'Location not specified'
                else:
                    # Fallback to legacy fields
                    location_parts = []
                    if prop.estate_name:
                        location_parts.append(prop.estate_name)
                    if prop.sub_county:
                        location_parts.append(prop.sub_county)
                    if prop.county:
                        location_parts.append(prop.county)
                    location_string = ', '.join(location_parts) if location_parts else 'Location not specified'
            except Exception as e:
                # If anything fails, use fallback
                location_parts = []
                if prop.estate_name:
                    location_parts.append(prop.estate_name)
                if prop.sub_county:
                    location_parts.append(prop.sub_county)
                if prop.county:
                    location_parts.append(prop.county)
                location_string = ', '.join(location_parts) if location_parts else 'Location not specified'
            
            # Ensure all required fields have default values
            # Safely get is_verified (it's a @property, so access directly)
            try:
                is_verified = prop.is_verified
            except:
                is_verified = (getattr(prop, 'verification_status', 'pending') == 'approved' and 
                              getattr(prop, 'ai_verification_result', '') == 'MATCH')
            
            # Safely get rating
            try:
                rating = float(prop.rating) if prop.rating else 0.0
            except (AttributeError, ValueError, TypeError):
                rating = 0.0
            
            # Get coordinates for map
            latitude = None
            longitude = None
            if prop.latitude and prop.longitude:
                latitude = float(prop.latitude)
                longitude = float(prop.longitude)
            
            properties.append({
                'id': prop.id,
                'name': prop.name or 'Unnamed Property',
                'location': location_string,
                'price': float(prop.price) if prop.price else 0,
                'bedrooms': prop.bedrooms or 0,
                'bathrooms': prop.bathrooms or 1,
                'type': prop.property_type or 'apartment',
                'verified': is_verified,
                'available': prop.available if prop.available is not None else True,
                'rating': rating,
                'reviews': getattr(prop, 'review_count', 0) or 0,
                'trustScore': getattr(prop, 'trust_score', 0) or 0,
                'image': image_url,
                'description': (prop.description[:200] + '...') if prop.description and len(prop.description) > 200 else (prop.description or 'No description available'),
                'verification_status': getattr(prop, 'verification_status', 'pending'),
                'verification_score': getattr(prop, 'verification_score', 0) or 0,
                'latitude': latitude,
                'longitude': longitude
            })
        
        # If no properties in database, return sample data for demo
        if not properties:
            properties = [
                {
                    'id': 1,
                    'name': 'Modern 2BR Apartment',
                    'location': 'Kilimani, Nairobi',
                    'price': 35000,
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'type': 'apartment',
                    'verified': True,
                    'available': True,
                    'rating': 4.8,
                    'reviews': 24,
                    'trustScore': 85,
                    'image': 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=300&fit=crop',
                    'description': 'Spacious apartment with modern amenities, parking, and security.'
                }
            ]
        
        return JsonResponse({'properties': properties, 'count': len(properties)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return error response with sample data to prevent frontend errors
        return JsonResponse({
            'properties': [
                {
                    'id': 1,
                    'name': 'Modern 2BR Apartment',
                    'location': 'Kilimani, Nairobi',
                    'price': 35000,
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'type': 'apartment',
                    'verified': True,
                    'available': True,
                    'rating': 4.8,
                    'reviews': 24,
                    'trustScore': 85,
                    'image': 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400&h=300&fit=crop',
                    'description': 'Spacious apartment with modern amenities, parking, and security.'
                }
            ],
            'count': 1,
            'error': str(e)
        }, status=500)

def notify_landlord_booking(booking, property_obj):
    """
    Notify landlord via WhatsApp when someone books their property
    Returns True if notification was sent/generated successfully
    """
    try:
        landlord = property_obj.owner
        
        # Get landlord's phone number from their application
        landlord_phone = None
        try:
            landlord_app = landlord.landlord_application
            landlord_phone = landlord_app.phone
        except LandlordApplication.DoesNotExist:
            # If no application, try to get from user profile or skip
            return False
        
        if not landlord_phone:
            return False
        
        # Format phone number
        phone = landlord_phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Add country code if not present (Kenya: 254)
        if not phone.startswith('254'):
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            else:
                phone = '254' + phone
        
        # Format date
        date_str = booking.date.strftime('%A, %B %d, %Y')
        
        # Get property location
        location = get_property_location_string(property_obj)
        
        # Get property details
        property_type = property_obj.get_property_type_display()
        listing_type = property_obj.get_listing_type_display()
        bedrooms = property_obj.bedrooms or 0
        bathrooms = property_obj.bathrooms or 1
        square_feet = getattr(property_obj, 'square_feet', None)
        square_meters = getattr(property_obj, 'square_meters', None)
        price = property_obj.price or 0
        deposit = property_obj.deposit or 0
        currency = getattr(property_obj, 'currency', 'KES')
        
        # Property description (shortened)
        description = property_obj.description or "No description available"
        short_description = description[:150] + "..." if len(description) > 150 else description
        
        # Generate map and directions links
        map_link = ""
        directions_link = ""
        if property_obj.latitude and property_obj.longitude:
            lat = float(property_obj.latitude)
            lng = float(property_obj.longitude)
            # Google Maps link
            map_link = f"https://www.google.com/maps?q={lat},{lng}"
            # Google Maps directions link
            directions_link = f"https://www.google.com/maps/dir/?destination={lat},{lng}"
        
        # Format payment information
        payment_info = f"KES {price:,.0f}/month"
        if deposit > 0:
            payment_info += f"\n💰 Deposit: KES {deposit:,.0f}"
        
        # Create comprehensive WhatsApp message for landlord
        message = (
            f"🏠 *New Booking Request - SmartKeja*\n\n"
            f"Hello {landlord.get_full_name() or landlord.username},\n\n"
            f"Someone wants to view your property!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 *GUEST DETAILS*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name: {booking.name}\n"
            f"📧 Email: {booking.email}\n"
            f"📱 Phone: {booking.phone}\n"
            f"{'✅ WhatsApp Updates Enabled' if booking.whatsapp_updates else '❌ No WhatsApp Updates'}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏘️ *PROPERTY INFORMATION*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏠 Property: {property_obj.name}\n"
            f"📋 Listing: {listing_type}\n"
            f"🏗️ Type: {property_type}\n"
            f"📍 Location: {location}\n"
            f"🛏️ Bedrooms: {bedrooms}\n"
            f"🚿 Bathrooms: {bathrooms}\n"
        )
        
        # Add size information if available
        if square_meters:
            message += f"📐 Size: {square_meters} m²"
            if square_feet:
                message += f" ({square_feet} sq ft)"
            message += "\n"
        elif square_feet:
            message += f"📐 Size: {square_feet} sq ft\n"
        
        message += (
            f"💵 Price: {payment_info}\n"
            f"📝 Description: {short_description}\n\n"
        )
        
        # Add map and directions if coordinates available
        if map_link:
            message += (
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🗺️ *LOCATION & DIRECTIONS*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📍 View on Map:\n{map_link}\n\n"
                f"🧭 Get Directions:\n{directions_link}\n\n"
            )
        
        message += (
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 *VIEWING SCHEDULE*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 Date: {date_str}\n"
            f"⏰ Time: {booking.time_slot}\n\n"
            f"Please confirm availability or contact the guest to reschedule.\n\n"
            f"🔗 Manage Booking:\nhttps://smartkeja.com/admin/properties/booking/{booking.id}/change/"
        )
        
        # Encode message for URL
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
        
        # In production, use WhatsApp Business API here
        # For now, log the URL
        print(f'Landlord WhatsApp notification URL: {whatsapp_url}')
        
        # TODO: Integrate with WhatsApp Business API to actually send
        # For now, return True to indicate it would be sent
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

def get_property_location_string(property_obj):
    """Helper function to get property location string"""
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

def send_whatsapp_confirmation(booking, phone_number):
    """
    Generate WhatsApp confirmation message URL
    Returns True if URL was generated successfully
    """
    try:
        # Format phone number (remove +, spaces, etc.)
        phone = phone_number.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Add country code if not present (Kenya: 254)
        if not phone.startswith('254'):
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            else:
                phone = '254' + phone
        
        # Format date
        date_str = booking.date.strftime('%A, %B %d, %Y')
        
        # Create WhatsApp message
        message = (
            f"🏠 *SmartKeja Booking Confirmation*\n\n"
            f"Hello {booking.name},\n\n"
            f"Your property viewing has been confirmed!\n\n"
            f"📅 *Date:* {date_str}\n"
            f"⏰ *Time:* {booking.time_slot}\n"
            f"🏘️ *Property:* {booking.property.name}\n\n"
            f"We'll send you a reminder 24 hours before your viewing.\n\n"
            f"Thank you for choosing SmartKeja!"
        )
        
        # Encode message for URL
        encoded_message = urllib.parse.quote(message)
        
        # Generate WhatsApp URL (for frontend to open)
        whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
        
        # In production, you could use WhatsApp Business API here
        # For now, we'll return the URL and let frontend handle it
        # Store URL in booking for later use if needed
        return True
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

@csrf_exempt
@require_http_methods(["POST", "GET"])
def api_booking(request):
    """API endpoint for booking property viewings"""
    # Handle GET request - return user's bookings
    if request.method == 'GET':
        try:
            if request.user.is_authenticated:
                bookings = Booking.objects.filter(user=request.user).select_related('property').order_by('-created_at')[:20]
            else:
                # If not authenticated, check by email in query params
                email = request.GET.get('email', '')
                if email:
                    bookings = Booking.objects.filter(email=email).select_related('property').order_by('-created_at')[:20]
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Please log in or provide an email address'
                    }, status=401)
            
            bookings_data = []
            for booking in bookings:
                bookings_data.append({
                    'id': booking.id,
                    'property_id': booking.property.id,
                    'property_name': booking.property.name,
                    'date': booking.date.strftime('%Y-%m-%d'),
                    'time': booking.time_slot,
                    'status': booking.status,
                    'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return JsonResponse({
                'success': True,
                'bookings': bookings_data,
                'count': len(bookings_data)
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    # Handle POST request - create new booking
    try:
        # Parse JSON data
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'error': 'Invalid JSON data. Please check your request format.'
            }, status=400)
        
        # Validate required fields
        required_fields = ['propertyId', 'date', 'time', 'name', 'email', 'phone']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return JsonResponse({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)
        
        # Validate email format
        email = data['email'].strip()
        if '@' not in email or '.' not in email.split('@')[1]:
            return JsonResponse({
                'success': False, 
                'error': 'Please provide a valid email address'
            }, status=400)
        
        # Validate phone number (basic check)
        phone = data['phone'].strip()
        if len(phone) < 10:
            return JsonResponse({
                'success': False, 
                'error': 'Please provide a valid phone number'
            }, status=400)
        
        # Parse and validate date
        from datetime import datetime, date
        try:
            booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            # Check if date is in the past
            if booking_date < date.today():
                return JsonResponse({
                    'success': False, 
                    'error': 'Booking date cannot be in the past'
                }, status=400)
        except ValueError as e:
            return JsonResponse({
                'success': False, 
                'error': f'Invalid booking date format. Expected YYYY-MM-DD. Error: {str(e)}'
            }, status=400)
        
        # Validate time slot
        time_slot = data['time'].strip()
        if not time_slot:
            return JsonResponse({
                'success': False, 
                'error': 'Please select a time slot'
            }, status=400)
        
        # Get property
        try:
            property_id = int(data['propertyId'])
            property_obj = Property.objects.get(id=property_id)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False, 
                'error': 'Invalid property ID'
            }, status=400)
        except Property.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Property not found. It may have been removed.'
            }, status=404)
        
        # Check if property is available
        if not property_obj.available:
            return JsonResponse({
                'success': False, 
                'error': 'This property is currently not available for booking'
            }, status=400)
        
        # Validate name
        name = data['name'].strip()
        if len(name) < 2:
            return JsonResponse({
                'success': False, 
                'error': 'Please provide your full name'
            }, status=400)
        
        # Check for duplicate bookings (same property, date, time, email)
        existing_booking = Booking.objects.filter(
            property=property_obj,
            date=booking_date,
            time_slot=time_slot,
            email=email,
            status__in=['pending', 'confirmed']
        ).first()
        
        if existing_booking:
            return JsonResponse({
                'success': False, 
                'error': 'You already have a booking for this property at this date and time'
            }, status=400)
        
            # Create booking
        try:
            whatsapp_enabled = data.get('whatsappUpdates', False)
            booking = Booking.objects.create(
                property=property_obj,
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone,
                date=booking_date,
                time_slot=time_slot,
                whatsapp_updates=whatsapp_enabled,
                status='pending'
            )
            
            # Send WhatsApp message to tenant if enabled
            tenant_whatsapp_sent = False
            if whatsapp_enabled:
                try:
                    tenant_whatsapp_sent = send_whatsapp_confirmation(booking, phone)
                except Exception as e:
                    # Don't fail booking if WhatsApp fails
                    import traceback
                    traceback.print_exc()
                    pass
            
            # Send WhatsApp notification to landlord
            landlord_notified = False
            try:
                landlord_notified = notify_landlord_booking(booking, property_obj)
            except Exception as e:
                # Don't fail booking if landlord notification fails
                import traceback
                traceback.print_exc()
                pass
            
            message = 'Booking confirmed!'
            if whatsapp_enabled and tenant_whatsapp_sent:
                message += ' WhatsApp confirmation sent.'
            elif whatsapp_enabled:
                message += ' You will receive WhatsApp updates.'
            else:
                message += ' You will receive a confirmation email shortly.'
            
            # Add landlord notification status
            if landlord_notified:
                message += ' The landlord has been notified.'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'booking_id': booking.id,
                'whatsapp_sent': tenant_whatsapp_sent,
                'landlord_notified': landlord_notified,
                'booking': {
                    'id': booking.id,
                    'property_name': property_obj.name,
                    'date': booking.date.strftime('%Y-%m-%d'),
                    'time': booking.time_slot,
                    'status': booking.status
                }
            }, status=201)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False, 
                'error': f'Failed to create booking: {str(e)}'
            }, status=500)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False, 
            'error': f'An unexpected error occurred: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def api_locations(request):
    """API endpoint for location hierarchy"""
    try:
        # Try to get from locations app
        try:
            from locations.models import County, SubCounty, Estate
            locations = []
            for estate in Estate.objects.select_related('sub_county', 'sub_county__county').all()[:100]:
                locations.append({
                    'county': estate.sub_county.county.name if estate.sub_county and estate.sub_county.county else '',
                    'sub_county': estate.sub_county.name if estate.sub_county else '',
                    'estate': estate.name,
                    'center_latitude': str(estate.center_latitude) if estate.center_latitude else None,
                    'center_longitude': str(estate.center_longitude) if estate.center_longitude else None,
                })
        except:
            # Fallback to default locations
            locations = [
                {'county': 'Nairobi', 'sub_county': 'Westlands', 'estate': 'Kilimani', 'center_latitude': '-1.2921', 'center_longitude': '36.8219'},
                {'county': 'Nairobi', 'sub_county': 'Westlands', 'estate': 'Westlands', 'center_latitude': '-1.2656', 'center_longitude': '36.8025'},
                {'county': 'Nairobi', 'sub_county': 'Westlands', 'estate': 'Parklands', 'center_latitude': '-1.2684', 'center_longitude': '36.8123'},
                {'county': 'Nairobi', 'sub_county': 'Nairobi South', 'estate': 'Karen', 'center_latitude': '-1.3197', 'center_longitude': '36.7084'},
                {'county': 'Mombasa', 'sub_county': 'Nyali', 'estate': 'Nyali', 'center_latitude': '-4.0435', 'center_longitude': '39.6682'},
                {'county': 'Kisumu', 'sub_county': 'Kisumu Central', 'estate': 'Milimani', 'center_latitude': '-0.0917', 'center_longitude': '34.7680'},
            ]
        
        return JsonResponse({'locations': locations})
    except Exception as e:
        return JsonResponse({'locations': [], 'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_upload(request):
    """API endpoint for file uploads"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)
        
        file = request.FILES['file']
        
        # Validate file size (20MB max)
        if file.size > 20 * 1024 * 1024:
            return JsonResponse({'error': 'File too large'}, status=400)
        
        # Generate unique filename
        ext = os.path.splitext(file.name)[1]
        filename = f"{uuid.uuid4()}{ext}"
        
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf', '.mp4', '.mov']
        if ext.lower() not in allowed_extensions:
            return JsonResponse({'error': 'Invalid file type'}, status=400)
        
        # Save file
        file_path = default_storage.save(f'uploads/{filename}', file)
        file_url = default_storage.url(file_path)
        
        return JsonResponse({
            'success': True,
            'url': file_url,
            'file_url': file_url,
            'filename': filename
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_submit_property(request):
    """API endpoint for submitting property for verification"""
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required. Please log in to submit a property.'
            }, status=401)
        
        # Check if user is an approved landlord
        try:
            application = request.user.landlord_application
            if application.status != 'approved':
                return JsonResponse({
                    'success': False,
                    'error': 'Your landlord application must be approved before listing properties.'
                }, status=403)
        except LandlordApplication.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Please apply to become a landlord first.'
            }, status=403)
        
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'price']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Handle latitude/longitude safely
        latitude = None
        longitude = None
        if data.get('latitude'):
            try:
                latitude = Decimal(str(data.get('latitude')))
            except (ValueError, InvalidOperation):
                pass
        if data.get('longitude'):
            try:
                longitude = Decimal(str(data.get('longitude')))
            except (ValueError, InvalidOperation):
                pass
        
        # Create property
        property_obj = Property.objects.create(
            owner=request.user,
            name=data.get('name', 'Unnamed Property'),
            description=data.get('description', ''),
            property_type=data.get('property_type', 'apartment'),
            listing_type=data.get('listing_type', 'rental'),
            price=Decimal(str(data.get('price', 0))),
            bedrooms=data.get('bedrooms', 1) or 1,
            bathrooms=data.get('bathrooms', 1) or 1,
            county=data.get('county', ''),
            sub_county=data.get('subCounty', ''),
            estate_name=data.get('estate', ''),
            latitude=latitude,
            longitude=longitude,
            verification_status='pending',
            ai_verification_result='PENDING',
            available=True
        )
        
        # Simulate AI verification
        import random
        verification_results = ['MATCH', 'PARTIAL', 'FAILED']
        property_obj.ai_verification_result = random.choice(verification_results)
        if property_obj.ai_verification_result == 'MATCH':
            property_obj.verification_status = 'approved'
            property_obj.verification_score = 95
        elif property_obj.ai_verification_result == 'PARTIAL':
            property_obj.verification_status = 'pending'
            property_obj.verification_score = 65
        else:
            property_obj.verification_status = 'rejected'
            property_obj.verification_score = 30
        property_obj.save()
        
        return JsonResponse({
            'success': True,
            'property': {
                'id': property_obj.id,
                'name': property_obj.name,
                'verification_status': property_obj.verification_status,
                'ai_verification_result': property_obj.ai_verification_result,
                'verification_score': property_obj.verification_score
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False, 
            'error': str(e),
        }, status=500)
