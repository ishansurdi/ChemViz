"""
URL Configuration for ChemViz API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AuthViewSet,
    DatasetViewSet,
    get_summary,
    get_data,
    generate_report,
    health_check
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'datasets', DatasetViewSet, basename='dataset')

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),
    
    # JWT Token endpoints
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Convenience endpoints for latest dataset
    path('summary/', get_summary, name='summary'),
    path('data/', get_data, name='data'),
    path('report/', generate_report, name='report'),
    
    # Router URLs
    path('', include(router.urls)),
]
