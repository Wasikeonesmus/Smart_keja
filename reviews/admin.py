from django.contrib import admin
from .models import Review, ReviewHelpful, TrustScore


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_type', 'property', 'reviewed_user', 'reviewer', 'rating', 'is_verified', 'is_approved', 'created_at']
    list_filter = ['review_type', 'rating', 'is_verified', 'is_approved', 'is_flagged']
    search_fields = ['property__name', 'reviewer__username', 'reviewed_user__username', 'title', 'comment']
    raw_id_fields = ['property', 'reviewed_user', 'reviewer', 'viewing_booking', 'airbnb_booking']
    readonly_fields = ['helpful_count']


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__comment', 'user__username']
    raw_id_fields = ['review', 'user']


@admin.register(TrustScore)
class TrustScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'overall_score', 'verification_score', 'review_score', 'transaction_score', 'is_verified_host', 'is_super_host', 'last_calculated']
    list_filter = ['is_verified_host', 'is_super_host', 'is_verified_landlord']
    search_fields = ['user__username']
    raw_id_fields = ['user']
    readonly_fields = ['last_calculated', 'created_at']
