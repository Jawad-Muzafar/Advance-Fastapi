import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class StudentDb(Base):
    __tablename__ = "students_record"

    student_id = Column(String, primary_key=True)
    name = Column(String(50), nullable=False)
    age = Column(Integer, nullable=False)
    course = Column(String(50), nullable=False)
    email = Column(String, unique=True, nullable=False)
    marks = Column(Float, nullable=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()