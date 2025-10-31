from rest_framework import generics
from .models import ServiceConfig
from .permissions import HasServiceConfigReadScope
from .serializers import ServiceConfigSerializer

class ServiceConfigListCreateView(generics.ListAPIView):
    permission_classes = [HasServiceConfigReadScope]
    serializer_class = ServiceConfigSerializer
    queryset = ServiceConfig.objects.filter(is_deprecated=False)
