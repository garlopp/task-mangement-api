from fastapi import FastAPI
from db import Base, engine
from routers import task, auth
from models import UserModel, TaskModel


Base.metadata.create_all(bind=engine)



app = FastAPI()


app.include_router(auth.router)
app.include_router(task.router)
