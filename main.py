from fastapi import FastAPI,HTTPException
import json
from typing import Dict,Literal
from pydantic import BaseModel,computed_field,EmailStr,Field
class Student(BaseModel):
    name: str
    age: int
    course: str
    marks: int
    email: EmailStr

    @computed_field
    @property
    def grade(self) -> str:
        if self.marks >= 90:
            return "A"
        elif self.marks >= 80:
            return "B"
        elif self.marks >= 70:
            return "C"
        elif self.marks >= 60:
            return "D"
        else:
            return "F"
# Home root endpoint
app = FastAPI()
@app.get("/home")
async def read_root():
    return {"Hello": "World"}
#-----------------------------------------------
# Data loading function
def load_data():
    with open("existing_students.json", "r") as file:
        data = json.load(file)
    return data
# ------------------------------------------------
# Student endpoints
@app.get("/students")
async def get_students():
    data = load_data()
    return data
# ---------------------------------------------------
@app.get("/students/sort")
async def sort_students(
    sort_by: Literal['id', 'age', 'grade'],
    order: Literal['asc', 'desc']
    ):
    if order=="asc":
        reverse=False
    else:
        reverse=True
    data = load_data()
    students = []
    for sid, details in data.items():
        student = Student(**details)
        students.append({**details, "id": sid, "grade": student.grade})
    return sorted(
        students,
        key=lambda x: x[sort_by],
        reverse=reverse
    )
# Get student by ID endpoint
@app.get("/student/{student_id}")
# Inserting keyvalue in info

async def get_student(student_id: str)-> Dict:
    data = load_data()
    if student_id in data:
        return data[student_id]
    else:
        raise HTTPException(status_code=404, detail="Student not found")
# ----------------------------------------------------------
@app.get("/students/paginate")
def paginate_students(page:int,limit:int):
    data=load_data()
    students=[]
    for student_id, details in data.items():
        details["id"] = student_id
        students.append(details)
    start_index=(page-1)*limit
    end_index=start_index+limit
    return students[start_index:end_index]
