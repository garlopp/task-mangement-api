from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from db import get_db
from models import UserModel
from utils.jwt import oauth2_scheme
from config import SECRET_KEY, ALGORITHM
from crud import user as user_crud

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # The user's email is the subject of the token
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError as e:
        print(f"JWT Decode Error: {e}")  # This will print the specific error to your console
        raise HTTPException(status_code=401, detail="Invalid token")

    user = user_crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user  # this is the real DB user instance
