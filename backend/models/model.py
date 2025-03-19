from datetime import datetime, date
from typing import List, Optional, Set
from sqlalchemy import Column, ForeignKey, DateTime, Date, JSON, Integer, String, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column


from ..utils.db import db

# class User(db.Model):
#     id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
#     name: Mapped[str]
#     email: Mapped[str]
#     password: Mapped[str]
#     username: Mapped[str]
#     role: Mapped[str]

# User: Mapped[User] = relationship()


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

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    approval: Mapped[bool]

    subjects: Mapped[Set["Subject"]] = relationship(
        secondary="instructor_subject", back_populates="instructors"
    )

    def __init__(self) -> None:
        super().__init__()

    def to_dict(self):
        return {
            "id": self.id,
        }


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
            "subject_id": self.subject_id,
            "subjects": self.subject,
        }


class Quiz(db.Model):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"))
    date_of_quiz: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    time_duration: Mapped[str] = mapped_column(
        String(5), nullable=False
    )  # HH:MM format
    remarks: Mapped[str] = mapped_column(String(500))
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="quizzes")
    questions: Mapped["Question"] = relationship("Question", back_populates="quiz")
    scores: Mapped["Score"] = relationship("Score", back_populates="quiz")


class Question(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[str] = mapped_column(ForeignKey("quizzes.id"))
    question_statement: Mapped[str] = mapped_column(String(500), nullable=False)
    options: Mapped[str] = mapped_column(JSON, nullable=False)
    correct_option: Mapped[int]
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")


class Score(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quizzes.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("student.id"))
    time_stamp_of_attempt: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.now()
    )
    total_scored: Mapped[float]

    quiz: Mapped["Quiz"] = relationship(back_populates="scores")
    user: Mapped[Student] = relationship(back_populates="scores")
