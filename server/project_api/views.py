from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.mail_utils import send_invitation_mail, send_invitation_accepted_mail, send_invitation_declined_mail
from project_api.models import Project, ProjectMember, Invitation
from server_api.models import Server
from server_api.serializers import ServerSerializer
from service_api.models import Service
from service_api.serializers import ServiceSerializer
from user_api.models import User
from .permissions import IsOwnerOrMember, ScopedMethodPermission, IsOwner
from .serializers import ProjectSerializer, ProjectMemberSerializer, InvitationSerializer

class ProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [ScopedMethodPermission]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(Q(owner=user) | Q(projectmember__user=user)).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.save(owner=user)
        ProjectMember.objects.create(project=project, user=user)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrMember, ScopedMethodPermission]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

class ProjectServerListView(generics.ListAPIView, generics.GenericAPIView):
    permission_classes = [IsOwnerOrMember, ScopedMethodPermission]
    serializer_class = ServerSerializer

    def get_queryset(self):
        project_id = self.kwargs['pk']
        project = Project.objects.get(id=project_id)

        self.check_object_permissions(self.request, project)

        return Server.objects.filter(project=project, is_deleted=False)

    def post(self, request, pk):
        server_id = request.data.get('server_id')
        server = Server.objects.get(id=server_id)
        project = Project.objects.get(id=pk)

        self.check_object_permissions(request, project)

        server.project = project
        server.save()

        serializer = ServerSerializer(server)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        server_id = request.data.get('server_id')
        server = Server.objects.get(id=server_id)
        project = Project.objects.get(id=pk)

        self.check_object_permissions(request, project)

        server.project = None
        server.save()
        return Response({"detail": "Server removed from the project"}, status=status.HTTP_200_OK)

class ProjectServiceListView(generics.ListAPIView, generics.GenericAPIView):
    permission_classes = [IsOwnerOrMember, ScopedMethodPermission]
    serializer_class = ServiceSerializer

    def get_queryset(self):
        project_id = self.kwargs['pk']
        project = Project.objects.get(id=project_id)

        self.check_object_permissions(self.request, project)

        return Service.objects.filter(project=project, is_deleted=False)

    def post(self, request, pk):
        service_id = request.data.get('service_id')
        service = Service.objects.get(id=service_id)
        project = Project.objects.get(id=pk)

        self.check_object_permissions(request, project)

        service.project = project
        service.save()

        serializer = ServiceSerializer(service)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        service_id = request.data.get('service_id')
        service = Service.objects.get(id=service_id)
        project = Project.objects.get(id=pk)

        self.check_object_permissions(request, project)

        service.project = None
        service.save()
        return Response({"detail": "Service removed from the project"}, status=status.HTTP_200_OK)

class ProjectMemberListView(generics.ListAPIView):
    permission_classes = [IsOwnerOrMember, ScopedMethodPermission]
    serializer_class = ProjectMemberSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id)
        self.check_object_permissions(self.request, project)
        return ProjectMember.objects.filter(project=project)

    def delete(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            self.check_object_permissions(request, project)

            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)

            try:
                member = ProjectMember.objects.get(project=project, user=user)
                member.delete()
                return Response({"detail": "User removed from project"}, status=status.HTTP_200_OK)
            except ProjectMember.DoesNotExist:
                return Response({"detail": "User is not a member of this project"}, status=status.HTTP_400_BAD_REQUEST)

        except Project.DoesNotExist:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class ProjectLeaveView(APIView):
    permission_classes = [IsOwnerOrMember,ScopedMethodPermission]

    def post(self, request, project_id):
        user = request.user

        try:
            project = Project.objects.get(id=project_id)
            member = ProjectMember.objects.filter(project=project, user=user).first()

            if not member:
                return Response({"detail": "User is not a member of this project"}, status=status.HTTP_400_BAD_REQUEST)

            if project.owner == user:
                return Response({"detail": "Project owner cant leave the project"}, status=status.HTTP_400_BAD_REQUEST)

            member.delete()
            return Response({"detail": "Successfully left the project"}, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

class ProjectInvitationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsOwner, ScopedMethodPermission]
    serializer_class = InvitationSerializer

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id)

        self.check_object_permissions(self.request, project)

        return Invitation.objects.filter(project=project)

    def post(self, request, project_id):
        email = request.data.get('email')

        if not email:
            return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            project = Project.objects.get(id=project_id)
            self.check_object_permissions(request,
                                          project)

        except Project.DoesNotExist:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        existing_invitation = Invitation.objects.filter(user=user, project=project).first()

        if existing_invitation:
            if existing_invitation.status == 'pending':
                return Response({"detail": "Invitation already exists and is pending"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "Invitation already exists"}, status=status.HTTP_400_BAD_REQUEST)

        invitation = Invitation.objects.create(user=user, project=project, status='pending')

        serializer = InvitationSerializer(invitation)

        send_invitation_mail(user, project)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvitationAcceptView(APIView):
    permission_classes = [ScopedMethodPermission]

    def post(self, request, project_id):
        user = request.user

        try:
            project = Project.objects.get(id=project_id)

            invitation = Invitation.objects.filter(user=user, project=project, status='pending').first()

            if not invitation:
                return Response({"detail": "No pending invitation found for this project"},
                                status=status.HTTP_404_NOT_FOUND)

            if invitation.status == 'accepted':
                return Response({"detail": "You have already accepted the invitation for this project"},
                                status=status.HTTP_400_BAD_REQUEST)

            invitation.status = 'accepted'
            invitation.save()

            ProjectMember.objects.create(user=user, project=project)

            send_invitation_accepted_mail(
                inviter=invitation.project.owner,
                invited_user=request.user,
                project=invitation.project
            )

            return Response({"detail": "Invitation accepted successfully"}, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

class InvitationDeclineView(APIView):
    permission_classes = [ScopedMethodPermission]

    def post(self, request, project_id):
        user = request.user

        try:
            project = Project.objects.get(id=project_id)

            invitation = Invitation.objects.filter(user=user, project=project, status='pending').first()

            if not invitation:
                return Response({"detail": "No pending invitation found for this project"},
                                status=status.HTTP_404_NOT_FOUND)

            if invitation.status == 'declined':
                return Response({"detail": "You have already declined the invitation for this project"},
                                status=status.HTTP_400_BAD_REQUEST)

            invitation.status = 'declined'
            invitation.save()

            send_invitation_declined_mail(
                inviter=invitation.project.owner,
                invited_user=request.user,
                project=invitation.project
            )

            return Response({"detail": "Invitation declined successfully"}, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({"detail": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
