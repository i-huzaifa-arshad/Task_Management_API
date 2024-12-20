from django.contrib import admin

from task_app.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "duration", "created_at")
    search_fields = ("title", "user__username")


admin.site.register(Task, TaskAdmin)
