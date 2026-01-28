"""
Django Admin Configuration for ChemViz Models
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Dataset, Equipment, EquipmentTypeDistribution, AnalyticsLog


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'uploaded_by', 
        'uploaded_at', 
        'total_equipment',
        'processing_status',
        'file_size_display'
    ]
    list_filter = ['processing_status', 'uploaded_at']
    search_fields = ['name', 'uploaded_by__username']
    readonly_fields = [
        'id',
        'uploaded_at',
        'row_count',
        'total_equipment',
        'avg_flowrate',
        'avg_pressure',
        'avg_temperature',
        'file_size'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'uploaded_by', 'uploaded_at', 'file')
        }),
        ('Statistics', {
            'fields': (
                'total_equipment',
                'row_count',
                'avg_flowrate',
                'avg_pressure',
                'avg_temperature'
            )
        }),
        ('Processing Status', {
            'fields': ('processing_status', 'error_message', 'file_size')
        }),
    )
    
    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        size_kb = obj.file_size / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f} KB"
        return f"{size_kb / 1024:.2f} MB"
    file_size_display.short_description = "File Size"


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        'equipment_name',
        'equipment_type',
        'flowrate',
        'pressure',
        'temperature',
        'dataset_name',
        'row_number'
    ]
    list_filter = ['equipment_type', 'dataset__uploaded_at']
    search_fields = ['equipment_name', 'equipment_type']
    readonly_fields = ['id', 'created_at']
    
    def dataset_name(self, obj):
        return obj.dataset.name
    dataset_name.short_description = "Dataset"


@admin.register(EquipmentTypeDistribution)
class EquipmentTypeDistributionAdmin(admin.ModelAdmin):
    list_display = [
        'equipment_type',
        'count',
        'percentage_display',
        'dataset_name',
        'avg_flowrate',
        'avg_pressure',
        'avg_temperature'
    ]
    list_filter = ['dataset__uploaded_at']
    search_fields = ['equipment_type', 'dataset__name']
    readonly_fields = ['id']
    
    def percentage_display(self, obj):
        return f"{obj.percentage:.1f}%"
    percentage_display.short_description = "Percentage"
    
    def dataset_name(self, obj):
        return obj.dataset.name
    dataset_name.short_description = "Dataset"


@admin.register(AnalyticsLog)
class AnalyticsLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'action',
        'user',
        'dataset_link',
        'ip_address'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = ['action', 'user__username', 'ip_address']
    readonly_fields = ['id', 'timestamp', 'user', 'action', 'dataset', 'details', 'ip_address']
    
    def dataset_link(self, obj):
        if obj.dataset:
            return format_html(
                '<a href="/admin/api/dataset/{}/change/">{}</a>',
                obj.dataset.id,
                obj.dataset.name
            )
        return "-"
    dataset_link.short_description = "Dataset"
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
