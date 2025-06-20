from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import get_db
from schemas import UserCreate, UserVerify, UserLogin, UserResponse, Token
from crud import user as user_crud
from utils import jwt
from crud.user import verify_password, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = user_crud.create_user(db, user.email, user.password)
    # TODO: Send OTP via email (for now, log it)
    print(f"OTP Code: {new_user.otp_code}")
    return new_user

@router.post("/verify", response_model=UserResponse)
def verify(user: UserVerify, db: Session = Depends(get_db)):
    verified_user = user_crud.verify_otp(db, user.email, user.otp_code)
    if not verified_user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return verified_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user.email)

    print("DB_USER", db_user)
    print("TYPE:", type(db_user))

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, db_user.hashed_password): # type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user.is_verified: # type: ignore
        raise HTTPException(status_code=403, detail="Account not verified")

    token = jwt.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
