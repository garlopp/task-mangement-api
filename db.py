from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "sqlite:///./auth.db" # Old SQLite connection
DATABASE_URL = "postgresql://postgres:blueface2580@localhost:5432/auth_db" 
# Replace with your actual PostgreSQL connection details
# Example: "postgresql://postgres:mypassword@localhost:5432/mydatabase"


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