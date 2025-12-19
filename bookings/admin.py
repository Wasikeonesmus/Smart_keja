from django.contrib import admin
from .models import ViewingBooking, AirbnbBooking, BookingCalendar


@admin.register(ViewingBooking)
class ViewingBookingAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'viewing_type', 'preferred_date', 'preferred_time', 'status', 'created_at']
    list_filter = ['status', 'viewing_type', 'preferred_date']
    search_fields = ['property__name', 'user__username', 'email', 'phone']
    raw_id_fields = ['property', 'user']
    date_hierarchy = 'preferred_date'


@admin.register(AirbnbBooking)
class AirbnbBookingAdmin(admin.ModelAdmin):
    list_display = ['property', 'guest', 'check_in_date', 'check_out_date', 'number_of_nights', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'payment_status', 'check_in_date']
    search_fields = ['property__name', 'guest__username', 'guest_email', 'guest_phone']
    raw_id_fields = ['property', 'guest', 'host']
    date_hierarchy = 'check_in_date'


@admin.register(BookingCalendar)
class BookingCalendarAdmin(admin.ModelAdmin):
    list_display = ['property', 'is_available', 'advance_booking_days', 'minimum_booking_days', 'updated_at']
    list_filter = ['is_available']
    search_fields = ['property__name']
    raw_id_fields = ['property']
