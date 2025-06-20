from fastapi import FastAPI
from db import Base, engine
from routers import task, user_auth
from models import UserModel, TaskModel


Base.metadata.create_all(bind=engine)



app = FastAPI()


app.include_router(user_auth.router)
app.include_router(task.router)
