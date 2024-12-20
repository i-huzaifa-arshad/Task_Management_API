from django.urls import path

from task_app.views import (CreateTaskView, CustomJwtAuthToken, DeleteTaskView,
                            GetTaskView, RetrieveTaskView, UpdateTaskView)

urlpatterns = [
    path("token/", CustomJwtAuthToken.as_view(), name="token_create"),
    path("tasks/create/", CreateTaskView.as_view(), name="task-create"),
    path("tasks/", GetTaskView.as_view(), name="get-tasks"),
    path("tasks/<int:task_id>/", RetrieveTaskView.as_view(), name="task-detail"),
    path("tasks/<int:task_id>/update/", UpdateTaskView.as_view(), name="task-update"),
    path("tasks/<int:task_id>/delete/", DeleteTaskView.as_view(), name="task-delete"),
]
