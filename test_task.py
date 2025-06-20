from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker # Import sessionmaker
from fastapi import FastAPI, status as http_status # Renamed for clarity
from sqlalchemy import create_engine
from sqlalchemy import create_engine, inspect # Import inspect
# from crud import task as task_crud # Not directly used in this test file, but imported in router
from schemas import TaskCreate, TaskUpdate, TaskResponse # TaskResponse for better type hinting
from utils.deps import get_db, get_current_user
import pytest
from routers import task as task_router

# Mock database dependency (example with in-memory SQLite)
@pytest.fixture(scope="function")
from models import TaskModel, UserModel, SharedTaskTokenModel, Base # Ensure models are imported before Base.metadata is used
def db_session():
    # Create an in-memory SQLite engine, allowing cross-thread access for testing
    # Define the engine ONCE with the correct arguments
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Create all tables in the in-memory database using this engine
    Base.metadata.create_all(bind=engine)

    # --- Debugging Check: Verify tables were created ---
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(f"\n--- Debug: Tables created in in-memory DB: {table_names} ---")
    assert 'task' in table_names, "The 'task' table was not created in the in-memory database."
    # ---------------------------------------------------
    # Create a session factory bound to this engine
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Create a session instance from the factory
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mock user dependency
def override_get_current_user():
    return UserModel(id=1, email="test@example.com")

app = FastAPI()
app.include_router(task_router.router)

# Create a TestClient instance
client = TestClient(app)

def test_create_task_success(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    # Use model_dump() for Pydantic V2+
    task_payload = TaskCreate(title="Test Task", description="A test task").model_dump() # type: ignore
    response = client.post("/tasks/", json=task_payload)
    assert response.status_code == http_status.HTTP_200_OK
    data = response.json()
    assert TaskResponse(**data)  # Validate response against schema
    assert data["title"] == "Test Task"
    assert data["description"] == "A test task"
    assert data["status"] == "pending"  # Default status from TaskModel
    assert "id" in data

def test_create_task_validation_error(db_session: Session): # Added db_session parameter
    # Test with missing required fields
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    task_data = {"description": "Missing title"}
    response = client.post("/tasks/", json=task_data) # type: ignore
    assert response.status_code == http_status.HTTP_422_UNPROCESSABLE_ENTITY
    error_data = response.json()
    assert "detail" in error_data
    assert any(err["loc"] == ["body", "title"] and err["type"] == "missing" for err in error_data["detail"])

# @pytest.mark.skip(reason="This test relies on creation succeeding, but we're forcing 200 for all") # Should be unskipped after fixes
def test_update_task_success(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create a task first
    initial_payload = TaskCreate(title="Task to Update", description="Initial description").model_dump() # type: ignore
    create_response = client.post("/tasks/", json=initial_payload)
    assert create_response.status_code == http_status.HTTP_200_OK
    task_id = create_response.json()["id"]

    # Now update the task
    update_payload = TaskUpdate(title="Updated Task", description="Updated description", status="completed", due_date="2024-12-31").model_dump(exclude_unset=True) # type: ignore
    update_response = client.put(f"/tasks/{task_id}", json=update_payload)
    assert update_response.status_code == http_status.HTTP_200_OK
 
    updated_task = update_response.json()
    assert TaskResponse(**updated_task) # Validate response
    assert updated_task["title"] == "Updated Task"
    assert updated_task["description"] == "Updated description"
    assert updated_task["status"] == "completed"

# @pytest.mark.skip(reason="This test relies on deletion succeeding, but we're forcing 200 for all") # Should be unskipped after fixes
def test_delete_task_success(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create a task to delete
    initial_payload = TaskCreate(title="Task to Delete", description="To be deleted").model_dump() # type: ignore
    create_response = client.post("/tasks/", json=initial_payload)
    assert create_response.status_code == http_status.HTTP_200_OK
    task_id = create_response.json()["id"]

    # Delete the task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == http_status.HTTP_200_OK
    assert delete_response.json() == {"msg": "Task deleted"}

    # Verify task is actually deleted by trying to fetch it
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == http_status.HTTP_404_NOT_FOUND

def test_read_tasks(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create a couple of tasks to ensure there's data # type: ignore
    client.post("/tasks/", json=TaskCreate(title="Task 1", description="First task").model_dump()) # type: ignore
    client.post("/tasks/", json=TaskCreate(title="Task 2", description="Second task").model_dump())

    response = client.get("/tasks/")
    assert response.status_code == http_status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2 # Check that at least the two created tasks are present
    for item in data:
        assert TaskResponse(**item) # Validate each item in the list
    assert data[0]["title"] == "Task 1" # Assuming order is preserved for this test
    assert data[1]["title"] == "Task 2"

def test_update_task_status(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create a task
    create_response = client.post("/tasks/", json={"title": "Task for Status Update", "description": "Update status to completed"}) # type: ignore # Removed completed: False
    assert create_response.status_code == http_status.HTTP_200_OK
    task_id = create_response.json()["id"]
    assert create_response.json()["status"] == "pending" # Initial status

    # Update the task status to completed
    update_payload = TaskUpdate(status="completed").model_dump(exclude_unset=True) # type: ignore # Simplified payload
    update_response = client.put(f"/tasks/{task_id}", json=update_payload)
    assert update_response.status_code == http_status.HTTP_200_OK

    updated_task = update_response.json()
    assert TaskResponse(**updated_task) # Validate response
    assert updated_task["status"] == "completed"

def test_update_task_status_invalid(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Create a task
    initial_payload = TaskCreate(title="Task for Invalid Status Update", description="Invalid status value").model_dump() # type: ignore
    create_response = client.post("/tasks/", json=initial_payload)
    assert create_response.status_code == http_status.HTTP_200_OK
    task_id = create_response.json()["id"]

    # Attempt to update the task with an invalid status value
    # Pydantic should catch this if 'status' is defined as str in TaskUpdate
    update_response = client.put(f"/tasks/{task_id}", json={"status": 123}) # type: ignore # Invalid type for status
    assert update_response.status_code == http_status.HTTP_422_UNPROCESSABLE_ENTITY
    # Optionally, check response.json()["detail"] for specific error messages
