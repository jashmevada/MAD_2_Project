from datetime import datetime, date, timedelta
from typing import List, Optional, Set
from sqlalchemy import Column, ForeignKey, DateTime, Date, Integer, String, Table, update
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.dialects.sqlite import JSON

from ..utils.db import db


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    role: Mapped[str]

    __mapper_args__ = {"polymorphic_identity": "user", "polymorphic_on": "role"}

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            # "email": self.email,
            "role": self.role,
        }


class Admin(User):
    id: Mapped[int] = mapped_column(ForeignKey(User.id), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

# Association table for Student-Quiz
class QuizAssignment(db.Model):
    __tablename__ = "quiz_assignment"
    
    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"), primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(default=datetime.now)
    accepted: Mapped[bool] = mapped_column(default=False)
    accepted_at: Mapped[Optional[datetime]]
    completed: Mapped[bool] = mapped_column(default=False)
    accepted_at: Mapped[Optional[datetime]]
    
    student: Mapped['Student'] = relationship(back_populates="quiz_assignments")
    quiz: Mapped['Quiz'] = relationship(back_populates="student_assignments")    

class Student(User):
    __mapper_args__ = {
        "polymorphic_identity": "student",
    }
    
    id: Mapped[int] = mapped_column(ForeignKey(User.id), primary_key=True)
    full_name: Mapped[str]
    qualification: Mapped[str]
    dob: Mapped[date]
    
    scores: Mapped["Score"] = relationship(back_populates="user")
    quiz_assignments: Mapped[Set['QuizAssignment']] = relationship(back_populates="student")

    

    def __repr__(self):
        return f"<Student {self.full_name}>"

    def accept_quiz(self, quiz_id):
        for assignment in self.quiz_assignments:
            if assignment.quiz_id == quiz_id:
                assignment.accepted = True
                assignment.accepted_at = datetime.now()
                return True
        return False
    
    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "qualification": self.qualification,
            "dob": self.dob,
        }


instructor_department = Table(
    "instructor_department",
    db.Model.metadata,
    Column("instructor_id", ForeignKey("instructors.id")),
    Column("department_id", ForeignKey("departments.id")),
)


class Instructor(User):
    __tablename__ = "instructors"

    __mapper_args__ = {
        "polymorphic_identity": "instructor",
    }

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    approval: Mapped[bool]
    qualification: Mapped[str]
    name: Mapped[str]
    department: Mapped[int] = mapped_column(ForeignKey("departments.id"))

    Idepartment: Mapped["Department"] = relationship(secondary="instructor_department", back_populates="instructors")

    def to_dict(self):
        return {
            "id": self.id,
            "approval": self.approval,
            "qualification": self.qualification,
            "name": self.name,
            "username": self.username,
            "dep_id": self.department,
            "email": self.email,
        }


# :TODO Add Department Model.
class Department(db.Model): 
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str] = mapped_column(default='')
    
    subjects: Mapped[List['Subject']] = relationship(cascade="all, delete")
    instructors: Mapped[Set["Instructor"]] = relationship(secondary="instructor_department", back_populates="Idepartment")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title, 
            "description": self.description
        }
    
class Subject(db.Model):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    department: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    
    chapters: Mapped[List["Chapter"]] = relationship(back_populates="subject", cascade="all, delete")
    Sdepartment: Mapped['Department'] = relationship(back_populates="subjects")
    
    @hybrid_property
    def instructors_list(self):
        return [assoc.instructor for assoc in self.instructors]

    @hybrid_property
    def no_of_chapters(self) -> int: 
        return len(self.chapters)
    
    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description, 'department': self.Sdepartment.title, "department_id": self.department}


class Chapter(db.Model):
    __tablename__ = "chapters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))

    subject: Mapped["Subject"] = relationship("Subject", back_populates="chapters")
    quizzes: Mapped["Quiz"] = relationship(back_populates="chapter", cascade="all, delete")

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "id": self.id,
            "subjects": self.subject.to_dict(),
        }

class Quiz(db.Model):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column (primary_key=True)
    title: Mapped[str]
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"))
    date_of_quiz: Mapped[datetime]
    time_duration: Mapped[str] = mapped_column(String(5))  # HH:MM format
    # remarks: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    no_student_attempt: Mapped[int] = mapped_column(default=0)
    
    chapter: Mapped["Chapter"] = relationship(back_populates="quizzes")
    questions: Mapped[Set["Question"]] = relationship("Question", back_populates="quiz", cascade="all, delete-orphan", passive_deletes=True)
    scores: Mapped[List["Score"]] = relationship("Score", back_populates="quiz", cascade="all, delete-orphan", passive_deletes=True)
    student_assignments: Mapped[Set['QuizAssignment']] = relationship(back_populates="quiz", cascade="all, delete-orphan")
    
    @hybrid_property
    def no_of_questions(self) -> int:
        return len(self.questions)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "chapter_id": self.chapter_id,
            "subject_id": self.chapter.subject.id,
            "date_of_quiz": self.date_of_quiz.strftime("%Y-%m-%d %H:%M:%S"), # .strftime("%Y-%m-%d %H:%M:%S")
            "time_duration": self.time_duration,
            # "remarks": self.remarks,
            "no_of_questions": self.no_of_questions,
            "subject": self.chapter.subject.name,
        }

class TimerSession(db.Model):
    __tablename__ = 'timer_sessions'
    
    id: Mapped[str] = mapped_column( primary_key=True)
    quiz_id: Mapped[int] = mapped_column( db.ForeignKey('quizzes.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'), nullable=False)
    start_time: Mapped[datetime] = mapped_column(default=datetime.now())
    duration_seconds: Mapped[int] 
    is_active: Mapped[bool] = mapped_column(default=True)
    
    
    quiz: Mapped['Quiz'] = relationship(backref='timer_sessions', cascade="all, delete")
    user: Mapped['User'] = relationship(backref='timer_sessions')
    
    @hybrid_property
    def end_time(self):
        if not self.start_time:
            return None
        return self.start_time + timedelta(seconds=self.duration_seconds)
    
    @hybrid_property
    def time_remaining(self):
        if not self.is_active:
            return 0
            
        now = datetime.now()
        end = self.end_time
        
        if now >= end:
            return 0
        
        return int((end - now).total_seconds())

class Question(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id"))
    question_statement: Mapped[str] = mapped_column(String(500))
    options: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON))
    correct_option: Mapped[int]
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "question_statement": self.question_statement,
            "options": self.options,
            "correct_option": self.correct_option,
        }


class Score(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("student.id"))
    time_stamp_of_attempt: Mapped[datetime] = mapped_column(default=datetime.now())
    # total_scored: Mapped[float] # convert into property compute by quiz and selected_options to get total scored.
    selected_options: Mapped[list[dict]] = mapped_column(MutableList.as_mutable(JSON))

    quiz: Mapped["Quiz"] = relationship(back_populates="scores")
    user: Mapped[Student] = relationship(back_populates="scores")

    @hybrid_property
    def total_scored(self) -> int: 
        """Count of correct Answer."""
        scores = 0 
        
        for i in self.selected_options:
            question_id = i.get('question_id')
            selected_option = i.get('selected_option') 
            
            ques: Question = Question.query.get(question_id)
            
            if int(selected_option) == ques.correct_option:
                scores += 1 
        
        return scores
    
    @hybrid_property
    def marks(self):
        """Marks are out of 100 or %"""
        return (self.total_scored / len(self.selected_options)) * 100
        
    def to_dict(self):
        return {
            "id": self.id,
            "selected_options": self.selected_options,
            "total_scored": self.total_scored,
            "date": self.time_stamp_of_attempt,
            "marks": self.marks,

        }
        
        
        