from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from schemas import TaskCreate, TaskResponse, TaskUpdate, ShareTaskRequest, TaskShareResponse
from crud import task as task_crud
# from crud.task import create_shared_task_token as shared_task_crud # Import shared_task_crud
from utils.deps import get_db, get_current_user
from utils.email_sender import send_task_share_email
from models import UserModel, TaskModel
from config import APP_BASE_URL


router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return task_crud.create_task(db, task, current_user.id)

@router.get("/", response_model=list[TaskResponse])
def read_tasks(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return task_crud.get_tasks(db, current_user.id)

@router.get("/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_task = task_crud.get_task(db, task_id, current_user.id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_task = task_crud.update_task(db, task_id, current_user.id, task)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    db_task = task_crud.delete_task(db, task_id, current_user.id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"msg": "Task deleted"}

@router.post("/{task_id}/share", response_model=TaskShareResponse, status_code=status.HTTP_200_OK)
def share_task_via_email(
    task_id: int,
    share_request: ShareTaskRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    db_task = task_crud.get_task(db, task_id=task_id, user_id=current_user.id) # type: ignore
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or you don't own this task")

    # Create a share token
    shared_token_obj = task_crud.create_shared_task_token(
        db=db,
        task_id=db_task.id, # type: ignore
        email_to_share_with=share_request.email_to_share_with
    )

    share_link = f"{APP_BASE_URL}/tasks/share/{shared_token_obj.token}"

    # Send the email (ensure your email utility and config are set up)
    try:
        send_task_share_email(
            recipient_email=share_request.email_to_share_with,
            task_title=db_task.title, # type: ignore
            share_link=share_link
        )
    except Exception as e:
        # Log the error, perhaps revert token creation or mark as unsent
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send email: {str(e)}")

    return TaskShareResponse(
        message="Task shared successfully. An email has been sent.",
        share_link_sent_to=share_request.email_to_share_with,
        task_id=db_task.id # type: ignore
    )
