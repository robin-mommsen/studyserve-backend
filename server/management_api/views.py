from django.utils import timezone
from rest_framework import generics
from infra.Terraform.container_manager import create_container, delete_container
from infra.Terraform.server_manager import create_server_terraform, delete_server_terraform
from infra.Terraform.power_manager import start, stop, shutdown
from management_api.permissions import AdminOnlyPermission, TeacherOrAdminPermission
from project_api.models import Project
from project_api.serializers import ProjectSerializer
from server_api.models import Server
from service_api.models import Service
from service_api.serializers import ServiceSerializer
from service_config_api.models import ServiceConfig
from service_config_api.serializers import ServiceConfigSerializer
from user_api.models import User
from server_config_api.models import ServerConfig
from server_api.serializers import ServerSerializer
from user_api.serializers import UserSerializer
from server_config_api.serializers import ServerConfigSerializer
from rest_framework.views import APIView
from .models import PlattformSettings, MaintenanceMessage, ScheduledCredit, Log
from .serializers import PlattformSettingsSerializer, CoinAdjustmentSerializer, MaintenanceMessageSerializer, \
    ScheduleCreditSerializer, LogSerializer
from django_q.tasks import async_task
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from project_api.models import Invitation
from project_api.serializers import InvitationSerializer

# Allgemeines Management
class ServerListView(generics.ListCreateAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [TeacherOrAdminPermission]


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            server = serializer.save(owner=request.user)
            server_id = server.id
            script_id = server.server_config_id
            ssh_key = server.ssh_keys.get("keys", [None])[0]

            try:
              server_config = ServerConfig.objects.get(id=script_id)
              script = server_config.script

            except ServerConfig.DoesNotExist:
               return Response({"detail": "ServerConfig not found"}, status=status.HTTP_400_BAD_REQUEST)

            async_task(create_server_terraform, server.hostname, server, server_id, script, ssh_key, hook='core.task_handlers.handle_server_create_result')

            return Response(self.get_serializer(server).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [TeacherOrAdminPermission]

    def perform_destroy(self, instance):
        server_id = instance.id
        script_id = instance.server_config_id

        try:
            server_config = ServerConfig.objects.get(id=script_id)
            script = server_config.script

        except ServerConfig.DoesNotExist:
            return Response({"detail": "ServerConfig not found"}, status=status.HTTP_400_BAD_REQUEST)

        async_task(delete_server_terraform, instance, server_id, script, "deleted_by_admin", hook='core.task_handlers.handle_server_delete_result')

        return Response(status=status.HTTP_200_OK)

class ServerActionView(APIView):
    permission_classes = [TeacherOrAdminPermission]

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

class ServiceActionView(APIView):
    permission_classes = [TeacherOrAdminPermission]

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


class ScheduleCreditListView(generics.ListCreateAPIView):
    queryset = ScheduledCredit.objects.all()
    serializer_class = ScheduleCreditSerializer
    permission_classes = [AdminOnlyPermission]

class ScheduleCreditDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ScheduledCredit.objects.all()
    serializer_class = ScheduleCreditSerializer
    permission_classes = [AdminOnlyPermission]

class ServiceListView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [TeacherOrAdminPermission]

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
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [TeacherOrAdminPermission]

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

        async_task(delete_container, instance, service_id, instance.hostname, tf_script, "deleted_by_admin", hook='core.task_handlers.handle_service_delete_result')

        return Response(status=status.HTTP_200_OK)


class ProjectListView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [TeacherOrAdminPermission]


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [AdminOnlyPermission()]
        return [TeacherOrAdminPermission()]

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AdminOnlyPermission()]
        return [TeacherOrAdminPermission()]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [AdminOnlyPermission()]
        return [TeacherOrAdminPermission()]

class ServerConfigListView(generics.ListCreateAPIView):
    serializer_class = ServerConfigSerializer
    permission_classes = [AdminOnlyPermission]

    def get_queryset(self):
        queryset = ServerConfig.objects.all()
        container = self.request.query_params.get('container')
        if container == 'true':
            queryset = queryset.filter(is_container=True)
        elif container == 'false':
            queryset = queryset.filter(is_container=False)
        return queryset


class ServerConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServerConfig.objects.all()
    serializer_class = ServerConfigSerializer
    permission_classes = [AdminOnlyPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_deprecated:
            return Response({"detail": "Cannot delete ServerConfig if 'is_deprecated' is False"},
                            status=status.HTTP_400_BAD_REQUEST)
        if Server.objects.filter(server_config_id=instance.id, is_deleted=False).exists():
            return Response({
                "detail": "ServerConfig cannot be deleted as long as there are servers using this config that are not deleted"},
                status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ServiceConfigListView(generics.ListCreateAPIView):
    queryset = ServiceConfig.objects.all()
    serializer_class = ServiceConfigSerializer
    permission_classes = [AdminOnlyPermission]

    def create(self, request, *args, **kwargs):
        server_config_id = request.data.get('server_config')
        try:
            config = ServerConfig.objects.get(id=server_config_id)
            if not config.is_container:
                return Response({"detail": "The given server_config_id is not a container"},
                                status=status.HTTP_400_BAD_REQUEST)
        except ServerConfig.DoesNotExist:
            return Response({"detail": "No ServerConfig found with the given id"}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

class ServiceConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceConfig.objects.all()
    serializer_class = ServiceConfigSerializer
    permission_classes = [AdminOnlyPermission]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.is_deprecated:
            return Response({"detail": "Cannot delete ServiceConfig if 'is_deprecated' is False"},
                            status=status.HTTP_400_BAD_REQUEST)
        if Service.objects.filter(service_config_id=instance.id, is_deleted=False).exists():
            return Response({
                "detail": "ServiceConfig cannot be deleted as long as there are services using this config that are not deleted"},
                status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class LogListView(generics.ListCreateAPIView):
    queryset = Log.objects.all().order_by('-created_at')
    serializer_class = LogSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            return [AdminOnlyPermission()]
        return [TeacherOrAdminPermission()]

class LogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [AdminOnlyPermission()]
        return [TeacherOrAdminPermission()]

class MaintenanceMessageListView(generics.ListCreateAPIView):
    queryset = MaintenanceMessage.objects.all()
    serializer_class = MaintenanceMessageSerializer
    permission_classes = [AdminOnlyPermission]

class MaintenanceMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaintenanceMessage.objects.all()
    serializer_class = MaintenanceMessageSerializer
    permission_classes = [AdminOnlyPermission]


class PublicMaintenanceMessageView(ListAPIView):
    serializer_class = MaintenanceMessageSerializer

    def get_queryset(self):
        return MaintenanceMessage.objects.filter(is_active=True).order_by('-created_at')

class InvitationListView(generics.ListCreateAPIView):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [AdminOnlyPermission()]
        return [TeacherOrAdminPermission()]

class InvitationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [AdminOnlyPermission()]
        return [TeacherOrAdminPermission()]


# Spezifisches Management

class PlattformSettingsView(APIView):
    permission_classes = [AdminOnlyPermission]

    def get_object(self):
        settings = PlattformSettings.objects.first()
        if not settings:
            settings = PlattformSettings.objects.create(
                coin_limit=10000,
                recharge_amount=500,
                recharge_interval=30,
                last_recharge=timezone.now()
            )

        return settings

    def get(self, request):
        settings = self.get_object()
        if not settings:
            return Response({"detail": "No PlattformSettings found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlattformSettingsSerializer(settings)
        return Response(serializer.data)

    def patch(self, request):
        settings = self.get_object()
        serializer = PlattformSettingsSerializer(settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            if 'coin_limit' in serializer.validated_data:
                new_limit = serializer.validated_data['coin_limit']
                User.objects.filter(coins__gt=new_limit).update(coins=new_limit)

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServerLimitationUpdateView(APIView):
    permission_classes = [TeacherOrAdminPermission]

    def patch(self, request):
        try:
            server_id = request.data.get("server_id")
            server = Server.objects.get(pk=server_id)
        except Server.DoesNotExist:
            return Response({"detail": "Server not found"}, status=status.HTTP_404_NOT_FOUND)

        unlimited = request.data.get("unlimited")

        if unlimited is None:
            return Response({"detail": "The 'unlimited' field is required"}, status=status.HTTP_400_BAD_REQUEST)

        server.unlimited = unlimited
        server.save()

        return Response(ServerSerializer(server).data, status=status.HTTP_200_OK)


class UserBalanceUpdateView(APIView):
    permission_classes = [TeacherOrAdminPermission]

    def patch(self, request):
        try:
            user = User.objects.get(pk=request.data.get('user_id'))
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CoinAdjustmentSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            reason = serializer.validated_data['reason']
            user.coins += amount
            user.save()

            return Response(
                UserSerializer(user).data
            , status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
