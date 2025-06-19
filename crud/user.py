from sqlalchemy.orm import Session
from models import UserModel
from utils.hash import hash_password
import random, datetime


def create_user(db: Session, email: str, password: str):
    otp_code = str(random.randint(100000, 999999))
    otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    user = UserModel(email=email, hashed_password=hash_password(password), otp_code=otp_code, otp_expiry=otp_expiry)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()

def verify_otp(db: Session, email: str, otp_code: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if user.otp_code == otp_code and user.otp_expiry > datetime.datetime.utcnow():  # type: ignore
        user.is_verified = True # type: ignore
        user.otp_code = None # type: ignore
        user.otp_expiry = None # type: ignore
        db.commit()
        db.refresh(user)
        return user
    return None
