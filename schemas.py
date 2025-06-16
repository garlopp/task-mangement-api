from pydantic import BaseModel

class Create_User(BaseModel):
    username: str
    password: str