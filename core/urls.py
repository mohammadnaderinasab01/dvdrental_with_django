from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularRedocView
from .swagger_views import CustomSchemaView, CustomSpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-panel/', include('admin_panel.urls')),
    path('store-staff-panel/', include('store_staff_panel.urls')),
    path('database-profiler/', include('database_profiler.urls')),
    path('film/', include('films.urls')),
    path('customer/', include('customer.urls')),
    path('payment/', include('payment.urls')),
    path('store/', include('store.urls')),
    path('api/schema/', CustomSchemaView.as_view(api_version='v2'), name='schema'),
    path('api/schema/swagger-ui/', CustomSpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('auth/', include('users.urls')),
]
