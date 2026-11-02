from fastapi import FastAPI,HTTPException
import json
from typing import Dict,Literal,Annotated
from pydantic import BaseModel, computed_field, EmailStr,Field
class Student(BaseModel):
    name: Annotated[str,Field(...,description="Name of the student",examples=["Ali"])]
    age: Annotated[int,Field(...,gt=0,lt=40,description="Age of the student",examples=["25"])]
    course: Annotated[str,Field(...,min_length=2,max_length=40,description="Age of the student",examples=["OOP"])]
    marks: Annotated[int,Field(...,ge=0,le=100,description="Marks of the student",examples=["50"])]
    email: Annotated[EmailStr,Field(...)]

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


# Data loading function
def load_data():
    with open("existing_students.json", "r") as file:
        return json.load(file)


@app.get("/students")
async def get_students():
    return load_data()


@app.get("/students/sort")
async def sort_students(
    sort_by: Literal["id", "age", "grade"],
    order: Literal["asc", "desc"],
):
    data = load_data()
    students = []
    for student_id, details in data.items():
        student = Student(**details)
        students.append({**details, "id": student_id, "grade": student.grade})

    return sorted(
        students,
        key=lambda student: student[sort_by],
        reverse=order == "desc",
    )


@app.get("/students/{student_id}")
async def get_student(student_id: str) -> Dict:
    data = load_data()
    if student_id not in data:
        raise HTTPException(status_code=404, detail="Student not found")
    return data[student_id]


@app.get("/students/paginate")
def paginate_students(page: int, limit: int):
    data = load_data()
    students = [
        {**details, "id": student_id}
        for student_id, details in data.items()
    ]
    start_index = (page - 1) * limit
    return students[start_index : start_index + limit]


def save_data(data):
    with open("existing_students.json", "w") as file:
        json.dump(data, file, indent=4)


@app.post("/create_student",status_code=201)

def create_student(id:str,student:Student):
    data=load_data()
    if id in load_data():
        raise HTTPException(
            status_code=400,
            detail=f"Student with this id {id} is already exist"
        )
    if any(details["email"]==student.email for details in data.values()):
        raise HTTPException(
            status_code=400,
            detail=f"This email is already exists "
        )
    data[id]=student.model_dump(exclude={"grade"})
    save_data(data)
    return{
        "message":"Student created successfully",
        "id":id,**data[id]}
    
