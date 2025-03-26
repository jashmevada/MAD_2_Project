from flask import Blueprint, app, current_app, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from backend.utils.db import db 

from ..models.model import Instructor, Student, User
from backend.utils.common import do_commit

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
        

def get_student_quizzes(id: int):
    student: Student = Student.query.get_or_404(id)
    
    return {'msg': 'Success'}, 200
    # return jsonify([i.to_dict() for i in student]), 200

bp.add_url_rule("/students", view_func=StudentsAPI.as_view("students_api"))
bp.add_url_rule("/students/<int:id>", view_func=SingleStudentAPI.as_view("single_student_api"))
bp.route("/students/<int:id>/quizzes", methods=["GET"])(get_student_quizzes)