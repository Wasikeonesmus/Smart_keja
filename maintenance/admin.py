from django.contrib import admin
from .models import MaintenanceIssue, MaintenanceUpdate, MaintenanceInspection, CaretakerAssignment, CaretakerAttendance


@admin.register(MaintenanceIssue)
class MaintenanceIssueAdmin(admin.ModelAdmin):
    list_display = ['property', 'reported_by', 'category', 'title', 'priority', 'status', 'assigned_to', 'reported_at']
    list_filter = ['status', 'priority', 'category', 'reported_at']
    search_fields = ['property__name', 'title', 'description', 'reported_by__username']
    raw_id_fields = ['property', 'reported_by', 'assigned_to']
    date_hierarchy = 'reported_at'


@admin.register(MaintenanceUpdate)
class MaintenanceUpdateAdmin(admin.ModelAdmin):
    list_display = ['issue', 'updated_by', 'status_change', 'created_at']
    list_filter = ['created_at']
    search_fields = ['issue__title', 'note', 'updated_by__username']
    raw_id_fields = ['issue', 'updated_by']


@admin.register(MaintenanceInspection)
class MaintenanceInspectionAdmin(admin.ModelAdmin):
    list_display = ['property', 'inspector', 'inspection_type', 'inspection_date', 'status', 'created_at']
    list_filter = ['status', 'inspection_type', 'inspection_date']
    search_fields = ['property__name', 'inspector__username', 'findings']
    raw_id_fields = ['property', 'inspector']
    date_hierarchy = 'inspection_date'


@admin.register(CaretakerAssignment)
class CaretakerAssignmentAdmin(admin.ModelAdmin):
    list_display = ['property', 'caretaker', 'start_date', 'end_date', 'is_active', 'issues_resolved', 'created_at']
    list_filter = ['is_active', 'start_date']
    search_fields = ['property__name', 'caretaker__username']
    raw_id_fields = ['property', 'caretaker']


@admin.register(CaretakerAttendance)
class CaretakerAttendanceAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'date', 'check_in_time', 'check_out_time', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['assignment__caretaker__username', 'assignment__property__name']
    raw_id_fields = ['assignment']
    date_hierarchy = 'date'
