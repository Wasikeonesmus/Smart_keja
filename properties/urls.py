from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('list/', views.list_property, name='list_property'),
    path('list/wizard/', views.list_property_wizard, name='list_property_wizard'),
    path('verification-demo/', views.verification_demo, name='verification_demo'),

    # Auth / landlord
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard-tenant.html', views.dashboard, name='dashboard_tenant'),  # Redirect old URL
    path('admin-panel/', views.custom_admin, name='custom_admin'),
    path('landlord/apply/', views.landlord_apply, name='landlord_apply'),
    path('landlord/status/', views.landlord_status, name='landlord_status'),

    # APIs
    path('api/properties/', views.api_properties, name='api_properties'),
    path('api/booking/', views.api_booking, name='api_booking'),
    path('api/locations/', views.api_locations, name='api_locations'),
    path('api/upload/', views.api_upload, name='api_upload'),
    path('api/submit-property/', views.api_submit_property, name='api_submit_property'),
]

