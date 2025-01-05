# To-Do List API

This project is a simple REST API for managing a to-do list. It is built using FastAPI, with data stored in an SQLite database.

## Features
- Create, read, update, and delete tasks.
- JWT-based authentication for secure access to API endpoints.
- In-memory SQLite database for task storage.

## Prerequisites
- Python 3.7 or higher installed on your system.
- SQLite software or any other database browser to inspect the database (optional).

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/todo-api.git
   cd todo-api
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```bash
   pip install fastapi uvicorn python-multipart pydantic
   ```

## Running the Project

1. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

   The server will start at `http://127.0.0.1:8000/`.

2. **Access the API documentation**:
   Open your browser and go to `http://127.0.0.1:8000/docs`. This will show the interactive Swagger UI for testing the API.

## API Endpoints

### 1. Authentication

- **POST /login**  
  Get a JWT token by providing valid credentials.

  **Request Body**:
  ```json
  {
    "username": "admin",
    "password": "password"
  }
  ```

  **Response**:
  ```json
  {
    "access_token": "your_generated_token"
  }
  ```

### 2. Tasks

- **POST /tasks**  
  Create a new task.  
  Requires JWT token.

  **Request Body**:
  ```json
  {
    "title": "Task Title",
    "description": "Task Description",
    "status": "pending"
  }
  ```

- **GET /tasks**  
  Fetch all tasks.  
  Requires JWT token.

- **GET /tasks/{task_id}**  
  Fetch a task by ID.  
  Requires JWT token.

- **PUT /tasks/{task_id}**  
  Update the status of a task.  
  Requires JWT token.

  **Request Body**:
  ```json
  {
    "status": "completed"
  }
  ```

- **DELETE /tasks/{task_id}**  
  Delete a task by ID.  
  Requires JWT token.

## Database

The tasks are stored in an SQLite database named `tasks.db`. You can inspect this database using any SQLite viewer tool.

## Debugging

- If you encounter any issues, check the server logs in the terminal for error messages.
- Ensure that you are using the correct database file by verifying the path printed when the server starts.

## License

This project is licensed under the MIT License. See the LICENSE file for details.