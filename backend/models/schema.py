from datetime import datetime, timedelta, time, date
from typing import Dict, List
from typing_extensions import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator, validator


class QueryRegisterModel(BaseModel):
    role: str

class InstructorCreateModel(BaseModel):
    user_role: Literal["instructor"]
    department: int | None = None
    qualification: str
    name: str

class StudentCreateModel(BaseModel):
    user_role: Literal["student"]
    dob: date
    qualification: str
    full_name: str


class UserModel(BaseModel):
    data: InstructorCreateModel | StudentCreateModel = Field(discriminator="user_role")
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class DepartmentModel(BaseModel):
    title: str 
    description: str 

class SubjectCreate(BaseModel):
    name: str
    department: int
    description: Optional[str] = None


class ChapterModel(BaseModel):
    name: str
    description: Optional[str] = None
    # subject: Optional[SubjectCreate] = None

# Chapters should have order or not??

# class ChapterCreate(BaseModel):
#     name: str
#     description: Optional[str] = None
#     subject_id: int

class QuestionModel(BaseModel):
    id: int | None = None
    question_statement: str
    # options: Dict[int , str]
    options: List[str]
    correct_option: int

class QuizCreateModel(BaseModel):
    title: str
    subject_id: int | None = None 
    chapter_id: int
    date_of_quiz: datetime
    time_duration: float
    created_by: int
    # time_duration: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    remarks: Optional[str] = None
    questions: List[QuestionModel]

class QuizQueryModel(BaseModel):
    subject_id: int | None = None

class TimerStartSchema(BaseModel):
    quiz_id: int
    duration: int  # in seconds
    
    @field_validator('duration')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('Duration must be positive')
        return v
    
# class QuestionCreate(BaseModel):
#     quiz_id: int
#     question_statement: str
#     options: List[str]
#     correct_option: int

# class ScoreCreate(BaseModel):
#     quiz_id: int
#     user_id: int
#     total_scored: float

class QuizAttempt(BaseModel):
    quiz_id: int
    timer_session_id: str
    answers: List[dict] 
