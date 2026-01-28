"""
Utility Functions for ChemViz API
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.conf import settings

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response data
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'type': exc.__class__.__name__,
            }
        }
        
        # Add detail if available
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                custom_response_data['error']['details'] = exc.detail
            else:
                custom_response_data['error']['message'] = str(exc.detail)
        
        response.data = custom_response_data
    else:
        # Log unhandled exceptions
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return response


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def success_response(data=None, message="Success", status_code=200):
    """
    Generate a consistent success response format
    """
    response_data = {
        'success': True,
        'message': message,
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status_code)


def error_response(message, errors=None, status_code=400):
    """
    Generate a consistent error response format
    """
    response_data = {
        'success': False,
        'error': {
            'message': message,
        }
    }
    
    if errors:
        response_data['error']['details'] = errors
    
    return Response(response_data, status=status_code)


def validate_csv_columns(df, required_columns):
    """
    Validate that DataFrame contains required columns
    Returns tuple: (is_valid, error_message, missing_columns)
    """
    df_columns = set(df.columns.str.strip().str.lower())
    required = set(col.lower() for col in required_columns)
    
    missing = required - df_columns
    
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}", list(missing)
    
    return True, None, []


def format_file_size(size_bytes):
    """
    Convert bytes to human-readable file size
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def clean_numeric_value(value):
    """
    Clean and convert value to float, handling various formats
    """
    if value is None or value == '':
        return None
    
    try:
        # Remove common non-numeric characters
        cleaned = str(value).strip().replace(',', '')
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def calculate_percentage(part, whole):
    """
    Calculate percentage safely
    """
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)
