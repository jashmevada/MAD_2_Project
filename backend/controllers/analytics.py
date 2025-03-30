from re import L
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required
from flask_pydantic import validate
from flask.views import MethodView

from backend.models.model import Instructor, Question, Quiz, Student

# from backend.utils.db import db
# from ..models.schema import ChapterModel
# from backend.utils.common import add_db, do_commit, cache
# from ..models.model import Subject, Chapter

bp = Blueprint("analytics", __name__, url_prefix="/api")

class AnalyticsAPI(MethodView): 
    def get(self):
        data = {
            "total_quizzes" : Quiz.query.count(),
            "total_questions" : Question.query.count(),
            "student_count" : Student.query.count(),
            "instructor_count": Instructor.query.count()
        }
    
        
        return {"msg": "no data", "but data": data}

class StudentAnayticsAPI(MethodView):
    def get(self):
        pass

class InstrutorsAnayticsAPI(MethodView):
    pass

# Routes
bp.add_url_rule("/analytics", view_func=AnalyticsAPI.as_view("analytics_api"))
bp.add_url_rule("/students/analytics", view_func=StudentAnayticsAPI.as_view("students_analytics_api"))
bp.add_url_rule("/students/analytics", view_func=InstrutorsAnayticsAPI.as_view("instr_analytics_api"))