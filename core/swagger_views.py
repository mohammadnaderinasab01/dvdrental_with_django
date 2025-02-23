from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny


class CustomSchemaView(SpectacularAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]


class CustomSpectacularSwaggerView(SpectacularSwaggerView):
    authentication_classes = []
    permission_classes = [AllowAny]
