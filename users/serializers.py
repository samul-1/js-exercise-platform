from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = (
            "id",
            "email",
            "username",
            "is_teacher",
            "course",
            "first_name",
            "last_name",
        )
