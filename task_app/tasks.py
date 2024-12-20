from celery import shared_task
from django.utils.timezone import localtime

from task_app.models import Task


@shared_task
def print_task_details():
    # Fetch all tasks created by user with ID = 1
    tasks = Task.objects.filter(user_id=1)

    if not tasks:
        return "No tasks found for user 1."

    task_details = []
    for task in tasks:
        created_at = localtime(task.created_at).strftime("%Y-%m-%d %H:%M:%S")
        updated_at = localtime(task.updated_at).strftime("%Y-%m-%d %H:%M:%S")
        task_details.append(
            f"Title: {task.title}, Duration: {task.duration}, Created At: {created_at}, Updated At: {updated_at}"
        )

    return "\n".join(task_details)
