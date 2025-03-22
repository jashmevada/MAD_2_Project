from datetime import datetime, date
from typing import List, Optional, Set
from sqlalchemy import Column, ForeignKey, DateTime, Date, Integer, String, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.mutable import MutableDict
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
            "email": self.email,
            "role": self.role,
        }


class Admin(User):
    id: Mapped[int] = mapped_column(ForeignKey(User.id), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }


class Student(User):
    id: Mapped[int] = mapped_column(ForeignKey(User.id), primary_key=True)
    full_name: Mapped[str]
    qualification: Mapped[str]
    dob: Mapped[date]
    # scores: Mapped[int] = mapped_column(ForeignKey("scores.id"))
    scores: Mapped["Score"] = relationship(back_populates="user")

    __mapper_args__ = {
        "polymorphic_identity": "student",
    }

    def __repr__(self):
        return f"<Student {self.full_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "qualification": self.qualification,
            "dob": self.dob,
            # "scores": [score.to_dict() for score in self.scores]
        }


instructor_subject = Table(
    "instructor_subject",
    db.Model.metadata,
    Column("instructor_id", ForeignKey("instructors.id")),
    Column("subject_id", ForeignKey("subjects.id")),
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
    subject: Mapped[int] = mapped_column(ForeignKey("subjects.id"))

    subjects: Mapped["Subject"] = relationship(
        secondary="instructor_subject", back_populates="instructors"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "approval": self.approval,
            "qualification": self.qualification,
            "name": self.name,
            "subject": self.subject,
            "email": self.email,
        }


# :TODO Add Department Model.
# class Department(db.Model): ...


class Subject(db.Model):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    department: Mapped[str]

    chapters: Mapped[List["Chapter"]] = relationship(back_populates="subject")
    instructors: Mapped[Set["Instructor"]] = relationship(
        secondary="instructor_subject", back_populates="subjects"
    )

    @property
    def instructors_list(self):
        return [assoc.instructor for assoc in self.instructors]

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Chapter(db.Model):
    __tablename__ = "chapters"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))

    subject: Mapped["Subject"] = relationship("Subject", back_populates="chapters")
    quizzes: Mapped["Quiz"] = relationship("Quiz", back_populates="chapter")

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "id": self.id,
            "subjects": self.subject.to_dict(),
        }


class Quiz(db.Model):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"))
    date_of_quiz: Mapped[datetime]
    time_duration: Mapped[str] = mapped_column(String(5))  # HH:MM format
    remarks: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="quizzes")
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="quiz"
    )
    scores: Mapped["Score"] = relationship("Score", back_populates="quiz")
    # created_by_user: Mapped["User"] = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "chapter_id": self.chapter_id,
            "subject": self.chapter.subject.name,
            "date_of_quiz": self.date_of_quiz,
            "time_duration": self.time_duration,
            "remarks": self.remarks,
            "question": [question.to_dict() for question in self.questions],
        }


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
    total_scored: Mapped[float] # convert into property compute by quiz and selected_options to get total scored.
    selected_options: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSON))

    quiz: Mapped["Quiz"] = relationship(back_populates="scores")
    user: Mapped[Student] = relationship(back_populates="scores")
