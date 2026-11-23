from fastapi import FastAPI,HTTPException,Query
from typing import Annotated,Literal
import json
from pydantic import BaseModel,Field,EmailStr
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

class Update_Student(BaseModel):
    name: Annotated[str | None, Field(default=None, min_length=2, max_length=50)]
    age: Annotated[int | None, Field(default=None, ge=16, le=30)]
    course: Annotated[str | None, Field(default=None, min_length=2, max_length=8)]
    email: Annotated[EmailStr | None, Field(default=None)]
    marks: Annotated[float | None, Field(default=None, ge=0, le=100)]
# Home root
@app.get("/")
def home_root():
    """
    This function is the home root of the API. It returns a welcome message when accessed.
    """
    return {"Welcome to the FastAPI application!"}

# Function to load the existing data
def load_data():
    """
    This function loads the existing data of the students
    """
    with open("students.json", "r") as file:
        data = json.load(file)
    return data

# Function to  save the data
def save_data(data):
    """
    This function will save the data 
    """
    with open("students.json","w") as file:
        json.dump(data,file,indent=4)


# This endpoint will load  the data
@app.get("/students")
def show_students():
    """
    This function will load the data
    """
    return load_data()

# This end point will sort the values amd pagination
@app.get("/students")
def sort(
    sort_by:Literal["name","age","marks"]=Query("name",description="The field to sort by. Can be 'name', 'age', or 'marks'."),
    order:Literal["asc","desc"]=Query("asc",description="The order of sorting. Can be 'asc' for ascending or 'desc' for descending."),
    page:int=Query(1,ge=1,description="Page number"),
    limit:int =Query(5,ge=5,le=100,description="Student per page")
):
    """
   -> This function will sort the students on name ,age and marks on asc and des
   -> Ask user how much data they want on one page
    """
    data=load_data()
    students_list = [{"student_id": sid, **info} for sid, info in data.items()]

    reverse=(order=="desc")
    students_list.sort(key=lambda x:x[sort_by].lower() if isinstance (x[sort_by],str) else x[sort_by],reverse=reverse)
    total=len(students_list)
    start=(page-1)*limit
    end=start+limit
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "students": students_list[start:end],
    }
# This endpoint will find student from existing data
@app.get("/students/{student_id}")
def find_student(student_id: str):
    """
    Find a student by ID.

    - Returns the student's data if found
    - Returns 404 if the student does not exist
    """
    data = load_data()

    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"student_id": student_id, **data[student_id]}

# This end point will create a new student
@app.post("/create_student",status_code=201)
def create_student(student:Student):
    """
    It will create a new student and use Student pydantic model to validate the data
    """
    data=load_data()
    if student.student_id in data:
        raise HTTPException(status_code=409,detail=f"Student with {student.student_id} id already exist")
    data[student.student_id]=student.model_dump(exclude={"student_id"})
    save_data(data)
    return {"message":"Student created "}

# End point to update the existing data of the student
@app.patch("/update_student/{student_id}")
def update_student(student_id: str, student_update: Update_Student):
    """
    Update an existing student.

    - Only the fields that are sent will be changed
    - Returns 404 if the student does not exist
    """
    data = load_data()

    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")

    changes = student_update.model_dump(exclude_unset=True,exclude_none=True)

    old_data = data[student_id].copy()
    data[student_id].update(changes)
    save_data(data)

    return {
        "message": "Student updated",
        "student_id": student_id,
        "old": old_data,
        "new": data[student_id],
    }
# End point to delete the student
@app.delete("/delete_student/{student_id}")
def delete_student(student_id:str):
    """
    ->Delete a student by its id
    """
    data=load_data()
    if student_id not in data:
        raise HTTPException(
            status_code=404,
            detail=f"Student with this {student_id} does not exist"
        )
    del data[student_id]
    save_data(data)
    return {
        "message":"Student deleted"
    }