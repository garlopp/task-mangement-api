from sqlalchemy.orm import Session
from models import UserModel
import random, datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str):
    return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, email: str, password: str):
    otp_code = str(random.randint(100000, 999999))
    otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
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
