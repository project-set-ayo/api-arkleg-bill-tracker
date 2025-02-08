from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserProfileSerializer

User = get_user_model()


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user  # Ensure users only update their own profile
