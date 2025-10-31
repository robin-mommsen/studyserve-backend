from rest_framework import generics
from .models import User
from .permissions import HasUserReadScope
from .serializers import UserSerializer

class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [HasUserReadScope]
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.request.user.id
        return User.objects.get(pk=user_id)