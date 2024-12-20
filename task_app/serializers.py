from rest_framework import serializers

from task_app.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "duration", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
