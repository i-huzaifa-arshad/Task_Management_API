from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from task_app.models import Task
from task_app.serializers import TaskSerializer


class CustomJwtAuthToken(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        if not User.objects.filter(username=username).exists():
            return Response({"detail": "Invalid username"}, status=401)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.validated_data["access"]
        return Response({"Token": access_token})


class CreateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(user=request.user).all().order_by("-id")[:4]
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class RetrieveTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = Task.objects.raw(
            "SELECT * FROM task_app_task WHERE id = %s AND user_id = %s",
            [task_id, request.user.id],
        )
        if task:
            serializer = TaskSerializer(task[0])
            return Response(serializer.data)
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


class UpdateTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        task = Task.objects.raw(
            "SELECT * FROM task_app_task WHERE id = %s AND user_id = %s",
            [task_id, request.user.id],
        )
        if task:
            task = task[0]
            new_title = request.data.get("title", task.title)
            Task.objects.raw(
                "UPDATE task_app_task SET title = %s WHERE id = %s AND user_id = %s",
                [new_title, task.id, request.user.id],
            )
            task.title = new_title
            task.save()
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


class DeleteTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id):
        task = Task.objects.raw(
            "SELECT * FROM task_app_task WHERE id = %s AND user_id = %s",
            [task_id, request.user.id],
        )
        if task:
            task[0].delete()
            return Response({"message": "Task deleted successfully"})
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
