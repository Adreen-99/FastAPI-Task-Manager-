from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel


#Instance:
app = FastAPI()

#dictonary ---- json
students = {
    1: {
        "name" : "john doe",
        "age" : 18,
        "gender" : "male",
        "year" : "year 12"

        },

    2: {
        "name" :  "elssie",
        "age"  : 14,
        "gender": "female",
        "year" : "year 9"

        }       
}

# new class model
class Student(BaseModel):
    name : str
    age : int
    gender : str
    year : str


# Get method
@app.get("/") #endpoint
def homepage():
    return {"name" : "First Line"}


@app.get("/get-student/{student_id}") #endpoint
def get_student(student_id: int):
    return students[student_id]


@app.get("/get-by-name/{student_id}") #endpoint
def get_by_name(* ,student_id: int ,name: Optional[str] = None, test : int):
    for student_id in students:
        if [student_id] ["name"] == name :
            return students [student_id]
    return{"Data" : "Not Found"}         




# Post method
@app.post("/create-student/{student_id}")
def create_student(student_id: int, student: Student):
    if student_id in students:
        return {"Error": "Student exists"}

    students[student_id] = student
    return students[student_id]
        
    

