from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "sqlite:///./auth.db"
DATABASE_URL = "postgresql://postgres:blueface2580@localhost:5432/auth_db" 



metadata = MetaData()
engine = create_engine(DATABASE_URL)
sessionLocal = sessionmaker(autocommit = False, autoflush= False, bind=engine)
Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()