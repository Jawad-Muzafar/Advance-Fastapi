import os
from dotenv import load_dotenv
from sqlalchemy import create_engine,text,Column,String ,INTEGER,FLOAT
from sqlalchemy.orm import DeclarativeBase,sessionmaker
# -> Geeting url form env
load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")
# ->Engine=the road towards the database
engine=create_engine(DATABASE_URL)
with engine.connect() as cn:
    version=cn.execute(text("Select version()")).scalar()
    print(f"Connected to the {version.split(",")[0]}")
# Base class that inherit froom the its parent class
class Base(DeclarativeBase):
    pass
# Student class to make a table for students record in Data base
class StudentDb(Base):
    __tablename__="students_record"
    student_id=Column(String,primary_key=True)
    name=Column(String(50),nullable=False)
    age=Column(INTEGER,nullable=False)
    marks=Column(INTEGER,nullable=False)
    course=Column(String(50),nullable=False)
    email=Column(String,unique=True,nullable=False)

# Creating table
Base.metadata.create_all(bind=engine)

# Creating Seasion 
session_local=sessionmaker(bind=engine)
db=session_local()

# Inserting student data in table
if db.get(StudentDb,"S001") is None:
    db.add(StudentDb(student_id="S001",
                                    name="Jawad Khan",
                                    age=25,
                                    course="Data Science",
                                    marks=80,
                                    email="jawadalmani11@gmail.com"
                     ))
db.commit()