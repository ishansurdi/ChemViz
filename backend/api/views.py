"""
API Views for ChemViz
Handles all REST API endpoints
"""
import logging
from rest_framework import viewsets, status, views
from rest_framework.decorators import action, api_view, permission_classes
from django.core.paginator import Paginator, EmptyPage
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Count, Avg
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from .models import Dataset, Equipment, EquipmentTypeDistribution, AnalyticsLog
from .serializers import (
    DatasetListSerializer,
    DatasetDetailSerializer,
    DatasetUploadSerializer,
    EquipmentSerializer,
    EquipmentTypeDistributionSerializer,
    SummaryStatisticsSerializer,
    UserSerializer,
    AnalyticsLogSerializer
)
from .services import DataProcessor, cleanup_old_datasets
from .utils import get_client_ip, success_response, error_response
from .pdf_generator import PDFReportGenerator
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.ViewSet):
    """
    Authentication endpoints for login, logout, and registration
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user"""
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email', '')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            
            # Validation
            if not username or not password:
                return error_response("Username and password are required", status_code=400)
            
            if User.objects.filter(username=username).exists():
                return error_response("Username already exists", status_code=400)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Log action
            AnalyticsLog.objects.create(
                user=user,
                action='USER_REGISTERED',
                ip_address=get_client_ip(request),
                details={'username': username}
            )
            
            return success_response(
                data={
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                },
                message="User registered successfully",
                status_code=201
            )
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """Authenticate user and return JWT tokens"""
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return error_response("Username and password are required", status_code=400)
            
            user = authenticate(username=username, password=password)
            
            if user is None:
                return error_response("Invalid credentials", status_code=401)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Log action
            AnalyticsLog.objects.create(
                user=user,
                action='USER_LOGIN',
                ip_address=get_client_ip(request),
                details={'username': username}
            )
            
            return success_response(
                data={
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                },
                message="Login successful"
            )
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout user (client should discard tokens)"""
        try:
            # Log action
            AnalyticsLog.objects.create(
                user=request.user,
                action='USER_LOGOUT',
                ip_address=get_client_ip(request)
            )
            
            return success_response(message="Logout successful")
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)


class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Dataset CRUD operations
    """
    queryset = Dataset.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DatasetListSerializer
        elif self.action == 'upload':
            return DatasetUploadSerializer
        return DatasetDetailSerializer
    
    def list(self, request):
        """
        GET /api/datasets/
        List all datasets (history)
        """
        try:
            datasets = self.get_queryset()
            serializer = self.get_serializer(datasets, many=True)
            
            return success_response(
                data=serializer.data,
                message=f"Retrieved {datasets.count()} datasets"
            )
            
        except Exception as e:
            logger.error(f"Error listing datasets: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/datasets/{id}/
        Get single dataset with details
        """
        try:
            dataset = self.get_object()
            serializer = self.get_serializer(dataset)
            
            return success_response(
                data=serializer.data,
                message="Dataset retrieved successfully"
            )
            
        except Dataset.DoesNotExist:
            return error_response("Dataset not found", status_code=404)
        except Exception as e:
            logger.error(f"Error retrieving dataset: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        POST /api/datasets/upload/
        Upload CSV file and process data
        """
        try:
            serializer = DatasetUploadSerializer(data=request.data)
            
            if not serializer.is_valid():
                return error_response(
                    "Invalid data",
                    errors=serializer.errors,
                    status_code=400
                )
            
            # Get uploaded file
            uploaded_file = serializer.validated_data['file']
            dataset_name = serializer.validated_data.get('name', uploaded_file.name)
            
            # Create dataset record
            dataset = Dataset.objects.create(
                name=dataset_name,
                file=uploaded_file,
                uploaded_by=request.user,
                file_size=uploaded_file.size,
                processing_status='pending'
            )
            
            # Process CSV data
            processor = DataProcessor(dataset)
            success, error_message = processor.process()
            
            if not success:
                return error_response(
                    f"Failed to process CSV: {error_message}",
                    status_code=400
                )
            
            # Cleanup old datasets (keep only last 5)
            cleanup_old_datasets()
            
            # Log action
            AnalyticsLog.objects.create(
                user=request.user,
                action='DATASET_UPLOADED',
                dataset=dataset,
                ip_address=get_client_ip(request),
                details={
                    'filename': dataset_name,
                    'size': uploaded_file.size,
                    'equipment_count': dataset.total_equipment
                }
            )
            
            # Return dataset details
            dataset.refresh_from_db()
            response_serializer = DatasetDetailSerializer(dataset)
            
            return success_response(
                data=response_serializer.data,
                message="CSV file uploaded and processed successfully",
                status_code=201
            )
            
        except Exception as e:
            logger.error(f"Error uploading dataset: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        GET /api/datasets/{id}/summary/
        Get summary statistics for a dataset
        """
        try:
            dataset = self.get_object()
            
            # Get type distributions
            distributions = EquipmentTypeDistribution.objects.filter(dataset=dataset)
            
            summary_data = {
                'dataset_id': dataset.id,
                'dataset_name': dataset.name,
                'uploaded_at': dataset.uploaded_at,
                'total_records': dataset.row_count,
                'total_equipment': dataset.total_equipment,
                'avg_flowrate': dataset.avg_flowrate,
                'avg_pressure': dataset.avg_pressure,
                'avg_temperature': dataset.avg_temperature,
                'equipment_type_distribution': EquipmentTypeDistributionSerializer(
                    distributions, many=True
                ).data
            }
            
            serializer = SummaryStatisticsSerializer(summary_data)
            
            # Log action
            AnalyticsLog.objects.create(
                user=request.user,
                action='SUMMARY_VIEWED',
                dataset=dataset,
                ip_address=get_client_ip(request)
            )
            
            return success_response(
                data=serializer.data,
                message="Summary statistics retrieved successfully"
            )
            
        except Dataset.DoesNotExist:
            return error_response("Dataset not found", status_code=404)
        except Exception as e:
            logger.error(f"Error getting summary: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """
        GET /api/datasets/{id}/data/
        Get all equipment records for a dataset (paginated)
        """
        try:
            dataset = self.get_object()
            
            # Get query parameters
            page_size = int(request.query_params.get('page_size', 100))
            page = int(request.query_params.get('page', 1))
            
            # Get equipment records
            equipment = Equipment.objects.filter(dataset=dataset)
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            paginated_equipment = equipment[start:end]
            
            serializer = EquipmentSerializer(paginated_equipment, many=True)
            
            return success_response(
                data={
                    'equipment': serializer.data,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_records': equipment.count(),
                        'total_pages': (equipment.count() + page_size - 1) // page_size
                    }
                },
                message=f"Retrieved {len(serializer.data)} equipment records"
            )
            
        except Dataset.DoesNotExist:
            return error_response("Dataset not found", status_code=404)
        except Exception as e:
            logger.error(f"Error getting data: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        GET /api/datasets/history/
        Get last 5 datasets
        """
        try:
            max_history = getattr(settings, 'MAX_DATASET_HISTORY', 5)
            datasets = Dataset.objects.all()[:max_history]
            serializer = DatasetListSerializer(datasets, many=True)
            
            return success_response(
                data=serializer.data,
                message=f"Retrieved {len(serializer.data)} recent datasets"
            )
            
        except Exception as e:
            logger.error(f"Error getting history: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)
    
    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """
        GET /api/datasets/{id}/report/
        Generate and download PDF report for a dataset
        """
        try:
            dataset = self.get_object()
            
            # Generate PDF
            generator = PDFReportGenerator(dataset)
            pdf_buffer = generator.generate()
            
            # Log action
            AnalyticsLog.objects.create(
                user=request.user,
                action='REPORT_GENERATED',
                dataset=dataset,
                ip_address=get_client_ip(request)
            )
            
            # Create HTTP response with PDF
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            filename = f"ChemViz_Report_{dataset.name.replace(' ', '_')}_{dataset.uploaded_at.strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Dataset.DoesNotExist:
            return error_response("Dataset not found", status_code=404)
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}", exc_info=True)
            return error_response(str(e), status_code=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summary(request):
    """
    GET /api/summary/
    Get summary for the most recent dataset
    """
    try:
        # Get the most recent dataset
        dataset = Dataset.objects.filter(processing_status='completed').first()
        
        if not dataset:
            return error_response("No datasets available", status_code=404)
        
        # Get type distributions
        distributions = EquipmentTypeDistribution.objects.filter(dataset=dataset)
        
        summary_data = {
            'dataset_id': dataset.id,
            'dataset_name': dataset.name,
            'uploaded_at': dataset.uploaded_at,
            'total_records': dataset.row_count,
            'total_equipment': dataset.total_equipment,
            'avg_flowrate': dataset.avg_flowrate,
            'avg_pressure': dataset.avg_pressure,
            'avg_temperature': dataset.avg_temperature,
            'equipment_type_distribution': EquipmentTypeDistributionSerializer(
                distributions, many=True
            ).data
        }
        
        serializer = SummaryStatisticsSerializer(summary_data)
        
        return success_response(
            data=serializer.data,
            message="Summary statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting summary: {str(e)}", exc_info=True)
        return error_response(str(e), status_code=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data(request):
    """
    GET /api/data/
    Get equipment data for the most recent dataset
    """
    try:
        # Get the most recent dataset
        dataset = Dataset.objects.filter(processing_status='completed').first()
        
        if not dataset:
            return error_response("No datasets available", status_code=404)
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        
        # Get equipment records
        equipment = Equipment.objects.filter(dataset=dataset).order_by('id')
        paginator = Paginator(equipment, page_size)
        
        try:
            equipment_page = paginator.page(page)
        except EmptyPage:
            equipment_page = paginator.page(paginator.num_pages)
        
        # Serialize equipment data
        serializer = EquipmentSerializer(equipment_page, many=True)
        
        return success_response({
            'dataset_name': dataset.name,
            'total_equipment': equipment.count(),
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'equipment': serializer.data
        })
    
    except Exception as e:
        return error_response(str(e), status_code=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """
    GET /api/report/
    Generate PDF report for the most recent dataset
    """
    try:
        # Get the most recent dataset
        dataset = Dataset.objects.filter(processing_status='completed').first()
        
        if not dataset:
            return error_response("No datasets available", status_code=404)
        
        # Generate PDF
        generator = PDFReportGenerator(dataset)
        pdf_buffer = generator.generate()
        
        # Log action
        AnalyticsLog.objects.create(
            user=request.user,
            action='REPORT_GENERATED',
            dataset=dataset,
            ip_address=get_client_ip(request)
        )
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        filename = f"ChemViz_Report_{dataset.name.replace(' ', '_')}_{dataset.uploaded_at.strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}", exc_info=True)
        return error_response(str(e), status_code=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analytics(request):
    """
    GET /api/analytics/
    Get analytics data
    """
    try:
        # Get query parameters
        page_size = int(request.query_params.get('page_size', 100))
        page = int(request.query_params.get('page', 1))
        
        # Get the most recent dataset
        dataset = Dataset.objects.filter(processing_status='completed').first()
        
        if not dataset:
            return error_response("No datasets available", status_code=404)
        
        # Get equipment records
        equipment = Equipment.objects.filter(dataset=dataset)
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_equipment = equipment[start:end]
        
        serializer = EquipmentSerializer(paginated_equipment, many=True)
        
        return success_response(
            data={
                'equipment': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_records': equipment.count(),
                    'total_pages': (equipment.count() + page_size - 1) // page_size
                }
            },
            message=f"Retrieved {len(serializer.data)} equipment records"
        )
        
    except Exception as e:
        logger.error(f"Error getting data: {str(e)}", exc_info=True)
        return error_response(str(e), status_code=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /api/health/
    Health check endpoint for monitoring
    """
    return success_response(
        data={
            'status': 'healthy',
            'version': '1.0.0',
            'database': 'connected'
        },
        message="System is operational"
    )
