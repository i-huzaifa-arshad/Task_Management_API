from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from task_app.models import Task


class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = APIClient()

        """ Get the token for testing API endpoints """
        url = reverse("token_create")
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        token = response.data["Token"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

    # Unit tests for CustomJwtAuthToken View
    def test_jwt_token_creation(self):
        """JWT token creation using valid credentials"""
        url = reverse("token_create")
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Token", response.data)

    def test_jwt_token_creation_invalid_credentials(self):
        """JWT token creation attempt using invalid credentials"""
        url = reverse("token_create")
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Unit tests for CreateTaskView
    def test_task_creation(self):
        """Task creation using valid data for authenticated user"""
        url = reverse("task-create")
        data = {"title": "Test Task", "duration": 30}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

    def test_task_creation_unauthorized(self):
        """Task creation attempt using valid data for unauthenticated user"""
        self.client.force_authenticate(user=None)
        url = reverse("task-create")
        data = {"title": "Test Task", "duration": 30}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Unit tests for GetTaskView
    def test_get_tasks(self):
        # Create 5 tasks
        for i in range(5):
            Task.objects.create(title=f"Task {i+1}", duration=30, user=self.user)

        url = reverse("get-tasks")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check only latest 4 tasks are returned
        self.assertEqual(len(response.data), 4)
        task_titles = [task["title"] for task in response.data]

        self.assertEqual(task_titles[0], "Task 5")
        self.assertEqual(task_titles[1], "Task 4")
        self.assertEqual(task_titles[2], "Task 3")
        self.assertEqual(task_titles[3], "Task 2")

    def test_get_tasks_unauthorized(self):
        """Test for unauthenticated user attempts to get tasks"""
        self.client.force_authenticate(user=None)
        url = reverse("get-tasks")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Unit tests for GetTaskView
    def test_task_retrieval(self):
        """Test if current user can access this task using task id"""
        task = Task.objects.create(title="Test Task", duration=30, user=self.user)
        url = reverse("task-detail", args=[task.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Task")

        """ Test if different user tries to access this task using task id """
        other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Task not found")

    def test_task_retrieval_unauthorized(self):
        """Task retrieval attempt for unauthorized user"""
        task = Task.objects.create(title="Test Task", duration=30, user=self.user)
        self.client.force_authenticate(user=None)
        url = reverse("task-detail", args=[task.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_task_retrieval_task_not_found(self):
        """Task retrieval attempt for non-existent task"""
        invalid_task_id = 999
        url = reverse("task-detail", args=[invalid_task_id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Task not found"})

    # Unit tests for UpdateTaskView
    def test_task_update(self):
        """Test if current user can update the task using task id"""
        task = Task.objects.create(title="Test Task", duration=30, user=self.user)
        url = reverse("task-update", args=[task.id])
        data = {"title": "Updated Task Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Task Title")

        """ Test if different user can update this task using task id """
        other_user = User.objects.create_user(
            username="anotheruser", password="anotherpassword"
        )
        self.client.force_authenticate(user=other_user)
        url = reverse("task-update", args=[task.id])
        data = {"title": "Updated Task Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Task not found")

    def test_task_update_only_title(self):
        """Test for only task title update"""
        task = Task.objects.create(title="Test Task", duration=30, user=self.user)
        url = reverse("task-update", args=[task.id])
        data = {"title": "Updated Task Title", "duration": 45}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Task Title")

        """ Check if the task duration remains the same """
        task.refresh_from_db()
        self.assertEqual(task.duration, 30)

    def test_task_update_unauthorized(self):
        """Test update attempt for unauthorized user"""
        task = Task.objects.create(title="Test Task", duration=30, user=self.user)
        self.client.force_authenticate(user=None)
        url = reverse("task-update", args=[task.id])
        data = {"title": "Updated Task Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_task_update_task_not_found(self):
        """Task update attempt for non-existent task"""
        invalid_task_id = 99
        url = reverse("task-update", args=[invalid_task_id])
        data = {"title": "Updated Task Title"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Task not found")

    # Unit test for DeleteTaskView
    def test_task_deletion(self):
        """Test if current user can delete the task"""
        task = Task.objects.create(title="Test Task", duration=30, user=self.user)
        url = reverse("task-delete", args=[task.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Task deleted successfully")

        """ Ensure the task no longer exists in the database """
        self.assertEqual(Task.objects.count(), 0)

        """ Test if different user can delete this task """
        other_user = User.objects.create_user(
            username="other_user", password="other_password"
        )
        self.client.force_authenticate(user=other_user)
        url = reverse("task-delete", args=[task.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Task not found")

    def test_task_deletion_unauthorized(self):
        """Task deletion attempt for unauthorized user"""
        task = Task.objects.create(title="Test Task", duration=30, user=self.user)
        self.client.force_authenticate(user=None)
        url = reverse("task-delete", args=[task.id])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_task_deletion_task_not_found(self):
        """Task deletion attempt for non-existent task"""
        task_id = 9999
        url = reverse("task-delete", args=[9999])
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Task not found")
