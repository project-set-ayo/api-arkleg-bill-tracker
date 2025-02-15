from django.contrib.auth.models import Group
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "full_name",
            "is_admin",
        ]
        extra_kwargs = {
            "email": {"read_only": True},
        }

    def get_is_admin(self, obj):
        return obj.groups.filter(name="admin").exists()

    def get_full_name(self, obj):
        return obj.get_full_name()
