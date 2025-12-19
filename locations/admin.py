from django.contrib import admin
from .models import County, SubCounty, Ward, Estate, LocationPin


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'region', 'center_latitude', 'center_longitude']
    search_fields = ['name', 'code']


@admin.register(SubCounty)
class SubCountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'county', 'center_latitude', 'center_longitude']
    list_filter = ['county']
    search_fields = ['name', 'county__name']


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ['name', 'sub_county', 'center_latitude', 'center_longitude']
    list_filter = ['sub_county__county', 'sub_county']
    search_fields = ['name']


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ['name', 'sub_county', 'area_type', 'is_popular', 'property_count']
    list_filter = ['area_type', 'is_popular', 'sub_county__county']
    search_fields = ['name', 'postal_code']
    raw_id_fields = ['ward', 'sub_county']


@admin.register(LocationPin)
class LocationPinAdmin(admin.ModelAdmin):
    list_display = ['latitude', 'longitude', 'estate', 'is_verified', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['address', 'landmark']
    raw_id_fields = ['estate']

