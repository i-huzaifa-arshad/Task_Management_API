# Dockerized Task Management Django Application (For Selteq)

This repository contains a Dockerized Task Management Django application that uses a Microsoft SQL Server database along with Redis and Celery for asynchronous task handling.

## Getting Started

### 1. Build and Start the Application

Run the following commands to build and start the application:
   ```
   docker compose build
   docker compose up -d
   ```

### 2. Setup the SQL Server Database

After building the images, follow these steps to set up the SQL Server database inside the Docker container:

1. Install SQL Server tools inside the sql_server container:
   ```
   docker exec -it -u root sql_server bash -c "apt update && apt install -y mssql-tools"
   ```
2. Create the selteq_db database:
   ```
   docker exec -it -u root sql_server bash -c "/opt/mssql-tools/bin/sqlcmd -S sql_server -U sa -P StrongPassword123! -Q 'CREATE DATABASE selteq_db'"
   ```
3. Restart the `app` container to apply changes
   ```
   docker-compose restart app
   ```

### 3. Apply migrations

1. Run Django migrations:
   ```
   docker-compose exec -it app python manage.py makemigrations
   docker-compose exec -it app python manage.py migrate
   ```
2. Restart the `app` container to apply changes
   ```
   docker-compose restart app
   ```
3. Create a superuser to access Django admin interface
   ```
   docker-compose exec -it app python manage.py createsuperuser
   ```
4. You can access the admin interface at: `http://127.0.0.1:8000/admin`

### 4. Inspect the Database (Optional)

To inspect the MS SQL database inside the Docker container, use the following steps:

1. Access the SQL Server inside the `sql_server` container:
   ```
   docker exec -it sql_server /opt/mssql-tools/bin/sqlcmd -S sql_server -U sa -P StrongPassword123!
   ```
2. Switch to the `selteq_db` database:
   ```sql
   1> USE selteq_db
   2> GO
   ```
3. List all tables:
   ```sql
   1> SELECT name FROM sys.tables
   2> GO
   ```
4. Query a specific table (For example `task_app_task` table to view the tasks)
   ```sql
   1> Select * from task_app_task
   2> GO
   ```

### API Endpoints

- `POST /token/` - Obtain a JWT token for authentication.
- `POST /tasks/create/` - Create a new task.
- `GET /tasks/` - Fetch all tasks.
- `GET /tasks/<int:task_id>/` - Retrieve the details of a specific task.
- `PATCH /tasks/<int:task_id>/update/` - Update a specific task.
- `DELETE /tasks/<int:task_id>/delete/` - Delete a specific task.

APIs can be tested using tools like Postman. Ensure the application is running at `http://127.0.0.1:8000` before testing.
