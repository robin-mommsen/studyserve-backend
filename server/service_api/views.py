from django.contrib.contenttypes.models import ContentType
from django.http.response import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from infra.Terraform.power_manager import start, stop, shutdown
from management_api.models import Log
from management_api.serializers import LogSerializer
from server_config_api.models import ServerConfig
from service_config_api.models import ServiceConfig
from .models import Service
from .permissions import IsOwner, ScopedMethodPermission
from .serializers import ServiceSerializer
from infra.Terraform.container_manager import create_container, delete_container
from django_q.tasks import async_task
from rest_framework.views import APIView

class ServiceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOwner, ScopedMethodPermission]
    serializer_class = ServiceSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return Service.objects.filter(owner_id=user_id, is_deleted=False)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            service = serializer.save(owner=request.user)
            service_id = service.id
            script_id = service.service_config_id
            ssh_key = ""

            try:
              ansible_script_obj = ServiceConfig.objects.get(id=script_id)
              tf_script_id = ansible_script_obj.server_config_id

              tf_script_obj = ServerConfig.objects.get(id=tf_script_id)

              if not tf_script_obj.is_container:
                 return Response({"detail": "The given server_config_id is not a container"},
                                 status=status.HTTP_400_BAD_REQUEST)

              ansible_script = ansible_script_obj.ansible_script
              tf_script = tf_script_obj.script

            except ServerConfig.DoesNotExist:
               return Response({"detail": "One of the configs not found"}, status=status.HTTP_400_BAD_REQUEST)

            async_task(create_container, service.hostname, service, service_id, tf_script, ansible_script, ssh_key, hook='core.task_handlers.handle_service_create_result')

            return Response(self.get_serializer(service).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwner, ScopedMethodPermission]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_object(self):
        service = super().get_object()
        self.check_object_permissions(self.request, service)
        return service

    def perform_destroy(self, instance):
        service_id = instance.id
        script_id = instance.service_config_id

        try:
            ansible_script_obj = ServiceConfig.objects.get(id=script_id)
            tf_script_id = ansible_script_obj.server_config_id

            tf_script_obj = ServerConfig.objects.get(id=tf_script_id)

            if not tf_script_obj.is_container:
                return Response({"detail": "The given server_config_id is not a container"},
                                status=status.HTTP_400_BAD_REQUEST)

            tf_script = tf_script_obj.script

        except ServerConfig.DoesNotExist:
            return Response({"detail": "One of the configs not found"}, status=status.HTTP_400_BAD_REQUEST)

        async_task(delete_container, instance, service_id, instance.hostname, tf_script, "deleted_by_owner", hook='core.task_handlers.handle_service_delete_result')

        return Response(status=status.HTTP_200_OK)

class ServiceActionView(APIView):
    permission_classes = [IsOwner, ScopedMethodPermission]

    def post(self, request, pk, action):
        try:
            service = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"detail": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

        service_id = service.id
        world_id = service.world_id
        service.in_progress = True
        service.save()

        if action == "start":
            async_task(start, service_id, world_id, service, action, "container",
                       hook='core.task_handlers.handle_service_action_result')

            return Response({"detail": "Service started"}, status=status.HTTP_200_OK)
        elif action == "stop":
            async_task(stop, service_id, world_id, service, action, "container",
                       hook='core.task_handlers.handle_service_action_result')

            return Response({"detail": "Service stopped"}, status=status.HTTP_200_OK)
        elif action == "shutdown":
            async_task(shutdown, service_id, world_id, service, action, "container",
                       hook='core.task_handlers.handle_service_action_result')

            return Response({"detail": "Service shut down"}, status=status.HTTP_200_OK)
        else:
            service.in_progress = False
            service.save()
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class ServiceLogListView(ListAPIView):
    permission_classes = [IsOwner, ScopedMethodPermission]
    serializer_class = LogSerializer

    def get_queryset(self):
        service_content_type = ContentType.objects.get_for_model(Service)
        try:
            service = Service.objects.get(pk=self.kwargs['pk'])

        except Service.DoesNotExist:
            raise Http404("Service not found")

        self.check_object_permissions(self.request, service)

        return Log.objects.filter(content_type=service_content_type, object_id=self.kwargs['pk'])