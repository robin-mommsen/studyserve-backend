from django.contrib.contenttypes.models import ContentType
from django.http.response import Http404
from django_q.tasks import async_task
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from infra.Terraform.server_manager import create_server_terraform, delete_server_terraform
from infra.Terraform.power_manager import start, stop, shutdown
from management_api.models import Log
from management_api.serializers import LogSerializer
from server_config_api.models import ServerConfig
from .models import Server
from .permissions import IsOwner, ScopedMethodPermission
from .serializers import ServerSerializer

class ServerListCreateView(generics.ListCreateAPIView):
    permission_classes = [ScopedMethodPermission]
    serializer_class = ServerSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return Server.objects.filter(owner_id=user_id, is_deleted=False)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            server = serializer.save(owner=request.user)
            server_id = server.id
            script_id = server.server_config_id
            ssh_key = server.ssh_keys.get("keys", [None])[0]

            try:
              server_config = ServerConfig.objects.get(id=script_id)

              if server_config.is_container:
                  return Response({"detail": "The given server_config_id is a container"},
                                  status=status.HTTP_400_BAD_REQUEST)

              script = server_config.script

            except ServerConfig.DoesNotExist:
               return Response({"detail": "ServerConfig not found"}, status=status.HTTP_400_BAD_REQUEST)

            async_task(create_server_terraform, server.hostname, server, server_id, script, ssh_key, hook='core.task_handlers.handle_server_create_result')

            return Response(self.get_serializer(server).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwner, ScopedMethodPermission]
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    def get_object(self):
        server = super().get_object()
        self.check_object_permissions(self.request, server)
        return server

    def perform_destroy(self, instance):
        server_id = instance.id
        script_id = instance.server_config_id

        try:
            server_config = ServerConfig.objects.get(id=script_id)
            script = server_config.script

        except ServerConfig.DoesNotExist:
            return Response({"detail": "ServerConfig not found"}, status=status.HTTP_400_BAD_REQUEST)

        async_task(delete_server_terraform, instance, server_id, script, "deleted_by_owner", hook='core.task_handlers.handle_server_delete_result')

        return Response(status=status.HTTP_200_OK)

class ServerActionView(APIView):
    permission_classes = [IsOwner, ScopedMethodPermission]

    def post(self, request, pk, action):
        try:
            server = Server.objects.get(id=pk)
        except Server.DoesNotExist:
            return Response({"detail": "Server not found"}, status=status.HTTP_404_NOT_FOUND)

        server_id = server.id
        world_id = server.world_id
        server.in_progress = True
        server.save()

        if action == "start":
            async_task(start, server_id, world_id, server, action, "server",
                       hook='core.task_handlers.handle_server_action_result')

            return Response({"detail": "Server started"}, status=status.HTTP_200_OK)
        elif action == "stop":
            async_task(stop, server_id, world_id, server, action, "server",
                       hook='core.task_handlers.handle_server_action_result')

            return Response({"detail": "Server stopped"}, status=status.HTTP_200_OK)
        elif action == "shutdown":
            async_task(shutdown, server_id, world_id, server, action, "server",
                       hook='core.task_handlers.handle_server_action_result')

            return Response({"detail": "Server shut down"}, status=status.HTTP_200_OK)
        else:
            server.in_progress = False
            server.save()
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class ServerLogListView(ListAPIView):
    permission_classes = [IsOwner, ScopedMethodPermission]
    serializer_class = LogSerializer

    def get_queryset(self):
        server_content_type = ContentType.objects.get_for_model(Server)
        try:
            server = Server.objects.get(pk=self.kwargs['pk'])

        except Server.DoesNotExist:
            raise Http404("Server not found")

        self.check_object_permissions(self.request, server)

        return Log.objects.filter(content_type=server_content_type, object_id=self.kwargs['pk'])