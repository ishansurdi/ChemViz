"""
Database Models for Chemical Equipment Data
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import uuid


class Dataset(models.Model):
    """
    Stores metadata for each uploaded CSV dataset.
    Maintains history of last 5 datasets as per requirements.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Original filename")
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='datasets',
        null=True,
        blank=True
    )
    uploaded_at = models.DateTimeField(default=timezone.now, db_index=True)
    file = models.FileField(
        upload_to='datasets/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        help_text="CSV file containing equipment data"
    )
    row_count = models.IntegerField(default=0, help_text="Number of equipment records")
    
    # Summary Statistics (cached for performance)
    total_equipment = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    
    # Metadata
    file_size = models.IntegerField(help_text="File size in bytes")
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Dataset"
        verbose_name_plural = "Datasets"
        indexes = [
            models.Index(fields=['-uploaded_at']),
            models.Index(fields=['processing_status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class Equipment(models.Model):
    """
    Stores individual equipment records parsed from CSV files.
    Each row in the CSV becomes an Equipment instance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.CASCADE, 
        related_name='equipment_records'
    )
    
    # Equipment Data Fields
    equipment_name = models.CharField(max_length=255, db_index=True)
    equipment_type = models.CharField(max_length=100, db_index=True)
    flowrate = models.FloatField(help_text="Flow rate value")
    pressure = models.FloatField(help_text="Pressure value")
    temperature = models.FloatField(help_text="Temperature value")
    
    # Optional fields for extended data
    unit_flowrate = models.CharField(max_length=20, blank=True, default="L/min")
    unit_pressure = models.CharField(max_length=20, blank=True, default="Bar")
    unit_temperature = models.CharField(max_length=20, blank=True, default="°C")
    
    # Metadata
    row_number = models.IntegerField(help_text="Original row number in CSV")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['dataset', 'row_number']
        verbose_name = "Equipment Record"
        verbose_name_plural = "Equipment Records"
        indexes = [
            models.Index(fields=['dataset', 'equipment_type']),
            models.Index(fields=['equipment_name']),
        ]
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"


class EquipmentTypeDistribution(models.Model):
    """
    Pre-computed distribution statistics for equipment types per dataset.
    Improves API performance by caching aggregations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.CASCADE, 
        related_name='type_distributions'
    )
    equipment_type = models.CharField(max_length=100)
    count = models.IntegerField()
    percentage = models.FloatField()
    
    # Aggregated statistics per type
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-count']
        verbose_name = "Equipment Type Distribution"
        verbose_name_plural = "Equipment Type Distributions"
        unique_together = ['dataset', 'equipment_type']
    
    def __str__(self):
        return f"{self.equipment_type}: {self.count} ({self.percentage:.1f}%)"


class AnalyticsLog(models.Model):
    """
    Audit log for tracking analytics operations and system events.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    action = models.CharField(max_length=50, db_index=True)
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Analytics Log"
        verbose_name_plural = "Analytics Logs"
    
    def __str__(self):
        return f"{self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
