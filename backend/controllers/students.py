from flask import Blueprint, app, current_app, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from ..models.model import Instructor, Student, User
from backend.models.schema import UserLogin, UserModel
from backend.utils.common import add_db

bp = Blueprint("students", __name__, url_prefix="/api")

class StudentsAPI(MethodView):
    
    def get(self):
        return [i.to_dict() for i in Student.query.all()], 200

bp.add_url_rule("/students", view_func=StudentsAPI.as_view("students_api"))