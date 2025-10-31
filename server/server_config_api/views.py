from rest_framework import generics
from .models import ServerConfig
from .permissions import HasServerConfigReadScope
from .serializers import ServerConfigSerializer

class ServerConfigListCreateView(generics.ListAPIView):
    permission_classes = [HasServerConfigReadScope]
    serializer_class = ServerConfigSerializer

    def get_queryset(self):
        queryset = ServerConfig.objects.filter(is_deprecated=False)
        container = self.request.query_params.get('container')
        if container == 'true':
            queryset = queryset.filter(is_container=True)
        elif container == 'false':
            queryset = queryset.filter(is_container=False)
        return queryset
