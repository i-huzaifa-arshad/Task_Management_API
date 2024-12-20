import time

from django.core.management.base import BaseCommand

from task_app.models import Task


class Command(BaseCommand):
    help = "Prints all tasks one by one every 10 seconds"

    def handle(self, *args, **kwargs):
        tasks = Task.objects.all()
        if not tasks:
            self.stdout.write("No tasks found in the database.")
            return

        for task in tasks:
            created_at = task.created_at.strftime("%Y-%m-%d %H:%M:%S")
            self.stdout.write(
                f"Task title: {task.title}, Duration: {task.duration}, Created At: {created_at}"
            )
            time.sleep(10)
