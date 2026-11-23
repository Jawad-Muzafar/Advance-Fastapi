from fastapi import FastAPI,HTTPException,Query,Depends,Path
from typing import Annotated,Literal
from pydantic import BaseModel,Field,EmailStr,ConfigDict,field_validator,computed_field
from database import StudentDb,get_db 
from sqlalchemy import func , select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
# Object of the fastapi class 
app=FastAPI()



# Base model of student
class Student(BaseModel):
    student_id:Annotated[str, Field(description="The ID of the student",examples=["S0011","S0012","S0013"])]
    name:Annotated[str, Field(description="The name of the student",examples=["Jawad","Sara"])]
    age:Annotated[int,Field(description="The age of the student",le=30,ge=16,examples=[18,20])]
    course:Annotated[str,Field(description="The course of the student",min_length=2,max_length=8,examples=["OOP","Math"])]
    email:Annotated[EmailStr,Field(description="The email of the student",examples=["jawad@example.com","sara@example.com"])]
    marks:Annotated[float,Field(description="The marks of the student",le=100,ge=0,examples=[70,80])]

@field_validator("name")
@classmethod
def check_name(cls,value):
    if not value.replace(" ","").isalpha():
        raise ValueError("Name must be contain only letters and spaces")
    return value.title




class Update_Student(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=2, max_length=50)]
    age: Annotated[int | None, Field(default=None, ge=16, le=30)]
    course: Annotated[str | None, Field(default=None, min_length=2, max_length=8)]
    email: Annotated[EmailStr | None, Field(default=None)]
    marks: Annotated[float | None, Field(default=None, ge=0, le=100)]
# Home root



class Student_responce(Student):
    model_config=ConfigDict(from_attributes=True)
    @computed_field
    @property
    def grade(self)->str:
        if self.marks >=90:
            return "A+"
        if self.marks>=80:
            return "A"
        if self.marks>=70:
            return "B"
        if self.marks>=60:
            return "C"
        if self.marks>=50:
            return "F"
        return "F"
@app.get("/",tags=["Home"])
def home_root():
    """
    This function is the home root of the API. It returns a welcome message when accessed.
    """
    return {"Welcome to the FastAPI application!"}




# Helper function
def to_dict(s:StudentDb)->dict:
    return{
        "student_id":s.student_id,
        "name":s.name,
        "age":s.age,
        "course":s.course,
        "marks":s.marks,
        "email":s.email,
    }


# Root for geeting student from data
@app.get("/student/{student_id}",response_model=Student_responce,tags=["Get"])
def get_student(
    student_id:str=Path(...,description="Enter id to find the student"),
    db:Session=Depends(get_db)
    ):
    student=db.get(StudentDb,student_id)
    if student is None:
        raise HTTPException(
            status_code=404,
            detail=f"Student with {student_id} not exist"
        )
    return to_dict(student)




@app.post("/createStudent",tags=["Create"])
def create_student(student:Student,responce_model=Student_responce,status_code=200,
                   db:Session=Depends(get_db)):
    if db.get(StudentDb,student.student_id):
        raise HTTPException(
            status_code=400,
            detail=f"Student with {student.student_id} already exists "
        )
    new_student=StudentDb(**student.model_dump())
    db.add(new_student)

    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=404,
            detail=f"Student with this email {student.email} already exists"
        )

    db.refresh(new_student)
    return new_student



@app.patch("/updateStudent/{student_id}",tags=["Update"])
def update_student(student_update:Update_Student,
                   student_id:str,
                   db:Session=Depends(get_db)
                   ):
    student=db.get(StudentDb,student_id)
    if not student:
        raise HTTPException(
            status_code=400,
            detail=f"Student with {student_id} does not exist"
        )
    changes=student_update.model_dump(exclude_unset=True)

    for field,values in changes.items():
        setattr(student,field,values)
    try:
            db.commit()
    except IntegrityError:
            raise HTTPException(
                status_code=404,
                detail=f"Student with this email {student.email} already exists"
            )
    
    db.refresh(student)
    return student




@app.delete("/deleteStudent/{student_id}",tags=["Delete"])
def delete_student(student_id:str=Path(...,description="Enter id to delete the student"),
                   db:Session=Depends(get_db)
):
    student=db.get(StudentDb,student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"Student with {student_id} does not exist"
        )
    db.delete(student)
    db.commit()
    return {"message":f"Student with {student_id} has been deleted successfully."}




@app.get("/students",tags=["Get"])
def get_students(
    sort_by: Literal["name", "age", "marks"] = Query("name", description="Kis base par sort karna hai"),
    order: Literal["asc", "desc"] = Query("asc", description="Ascending ya descending"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(5, ge=1, le=100, description="Ek page mein kitne students"),
    db: Session = Depends(get_db),
):
    """
    Get students with sorting and pagination.

    - **sort_by**: name, age or marks
    - **order**: asc or desc
    - **page**: page number (starts from 1)
    - **limit**: students per page
    """
    # 1. Sorting ka column chunein
    column = getattr(StudentDb, sort_by,)
    column = column.desc() if order == "desc" else column.asc()

    # 2. Kul students ginein
    total = db.scalar(select(func.count()).select_from(StudentDb))

    # 3. Sort + pagination ek hi query mein
    query = (
        select(StudentDb)
        .order_by(column)
        .limit(limit)
        .offset((page - 1) * limit)
    )
    students = db.scalars(query).all()

    # 4. Response
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "students": [to_dict(s) for s in students],
    }