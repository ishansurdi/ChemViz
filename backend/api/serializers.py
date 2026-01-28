"""
Serializers for ChemViz API
Transform Django models to/from JSON for REST API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, Equipment, EquipmentTypeDistribution, AnalyticsLog


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment records"""
    
    class Meta:
        model = Equipment
        fields = [
            'id',
            'equipment_name',
            'equipment_type',
            'flowrate',
            'pressure',
            'temperature',
            'unit_flowrate',
            'unit_pressure',
            'unit_temperature',
            'row_number'
        ]
        read_only_fields = ['id']


class EquipmentTypeDistributionSerializer(serializers.ModelSerializer):
    """Serializer for equipment type distribution statistics"""
    
    class Meta:
        model = EquipmentTypeDistribution
        fields = [
            'equipment_type',
            'count',
            'percentage',
            'avg_flowrate',
            'avg_pressure',
            'avg_temperature'
        ]


class DatasetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dataset list view"""
    uploaded_by_username = serializers.CharField(
        source='uploaded_by.username',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'uploaded_by_username',
            'uploaded_at',
            'total_equipment',
            'processing_status',
            'file_size'
        ]
        read_only_fields = fields


class DatasetDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single dataset view"""
    uploaded_by = UserSerializer(read_only=True)
    type_distributions = EquipmentTypeDistributionSerializer(many=True, read_only=True)
    equipment_count = serializers.IntegerField(
        source='equipment_records.count',
        read_only=True
    )
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'uploaded_by',
            'uploaded_at',
            'file',
            'row_count',
            'total_equipment',
            'equipment_count',
            'avg_flowrate',
            'avg_pressure',
            'avg_temperature',
            'file_size',
            'processing_status',
            'error_message',
            'type_distributions'
        ]
        read_only_fields = fields


class DatasetUploadSerializer(serializers.ModelSerializer):
    """Serializer for CSV file upload"""
    file = serializers.FileField(required=True)
    
    class Meta:
        model = Dataset
        fields = ['file', 'name']
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file extension
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size exceeds maximum allowed size of 10MB. "
                f"Current size: {value.size / (1024 * 1024):.2f}MB"
            )
        
        return value
    
    def validate_name(self, value):
        """Validate dataset name"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Dataset name cannot be empty.")
        return value.strip()


class SummaryStatisticsSerializer(serializers.Serializer):
    """Serializer for summary statistics response"""
    total_equipment = serializers.IntegerField()
    avg_flowrate = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    equipment_type_distribution = EquipmentTypeDistributionSerializer(many=True)
    dataset_info = serializers.SerializerMethodField()
    
    def get_dataset_info(self, obj):
        return {
            'id': str(obj.get('dataset_id')),
            'name': obj.get('dataset_name'),
            'uploaded_at': obj.get('uploaded_at'),
            'total_records': obj.get('total_records')
        }


class AnalyticsLogSerializer(serializers.ModelSerializer):
    """Serializer for analytics logs"""
    user_username = serializers.CharField(
        source='user.username',
        read_only=True,
        allow_null=True
    )
    dataset_name = serializers.CharField(
        source='dataset.name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = AnalyticsLog
        fields = [
            'id',
            'timestamp',
            'user_username',
            'action',
            'dataset_name',
            'details',
            'ip_address'
        ]
        read_only_fields = fields
