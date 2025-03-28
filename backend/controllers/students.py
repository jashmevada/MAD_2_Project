from datetime import datetime
from flask import Blueprint, app, current_app, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from backend.utils.db import db 

from ..models.model import Instructor, Quiz, QuizAssignment, Student, User
from backend.utils.common import add_db, do_commit

bp = Blueprint("students", __name__, url_prefix="/api")

class StudentsAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]

    def get(self):
        return [i.to_dict() for i in Student.query.all()], 200


class SingleStudentAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]
    def get(self, id):
        return Student.query.get_or_404(id).to_dict(), 200

    def delete(self,id):
        student = Student.query.get_or_404(id)
        db.session.delete(student)
        return do_commit("Student deleted successfully", "Student could not be deleted")

def accept_quiz(id:int):
    quiz_id: int | None = request.args.get("q_id", type=int)
    
    student: Student = Student.query.get_or_404(id)
    quiz: Quiz = Quiz.query.get_or_404(quiz_id)
    qass = QuizAssignment(student=student, quiz=quiz)
    
    msg,c1 = add_db([qass])
    
    if quiz_id and c1 == 200:
        student.accept_quiz(quiz_id)
        return do_commit()
    
    return {'msg': 'No Quiz ID'}, 400 


@jwt_required()
def get_student_quizzes(id: int):
    student: Student = Student.query.get_or_404(id)
    quiz_set = set()
    print(student.quiz_assignments)
    for i in student.quiz_assignments:
        # print(i.accepted)
        if i.accepted:
            quiz_set.add(i)
    print(quiz_set)
    return [i.quiz.to_dict() for i in quiz_set]

bp.add_url_rule("/students", view_func=StudentsAPI.as_view("students_api"))
bp.add_url_rule("/students/<int:id>", view_func=SingleStudentAPI.as_view("single_student_api"))
bp.route("/students/<int:id>/quizzes", methods=["GET"])(get_student_quizzes)
bp.route("/students/<int:id>/accept_quiz")(accept_quiz)