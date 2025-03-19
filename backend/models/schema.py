from datetime import datetime, timedelta, time, date
from typing_extensions import Annotated, Literal, Optional, Union
from pydantic import BaseModel, Field


class QueryRegisterModel(BaseModel):
    role: str


class InstructorCreateModel(BaseModel):
    user_role: Literal["instructor"]
    subjects: list[str]


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


class SubjectCreate(BaseModel):
    name: str
    department: str
    description: Optional[str] = None


class ChapterModel(BaseModel):
    name: str
    description: Optional[str] = None
    subject_id: str
    subject: Optional[SubjectCreate] = None


# class ChapterCreate(BaseModel):
#     name: str
#     description: Optional[str] = None
#     subject_id: int

# class QuizCreate(BaseModel):
#     chapter_id: int
#     date_of_quiz: datetime
#     time_duration: str = Field(..., regex=r'^\d{2}:\d{2}$')
#     remarks: Optional[str] = None

# class QuestionCreate(BaseModel):
#     quiz_id: int
#     question_statement: str
#     options: List[str]
#     correct_option: int

# class ScoreCreate(BaseModel):
#     quiz_id: int
#     user_id: int
#     total_scored: float

# class QuizAttempt(BaseModel):
#     quiz_id: int
#     answers: List[int]
