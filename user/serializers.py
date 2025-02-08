from django.contrib.auth.models import Group
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["email", "phone_number", "is_admin"]
        extra_kwargs = {
            "email": {"read_only": True},
        }

    def get_is_admin(self, obj):
        return obj.groups.filter(name="admin").exists()
