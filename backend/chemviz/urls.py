"""
ChemViz URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('test/', TemplateView.as_view(template_name='test_api.html'), name='api_tester'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "ChemViz Administration"
admin.site.site_title = "ChemViz Admin Portal"
admin.site.index_title = "Welcome to ChemViz Administration"
