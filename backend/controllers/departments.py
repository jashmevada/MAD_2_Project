from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from backend.utils.common import add_db, do_commit, cache
from ..models.model import Department, Subject

bp = Blueprint("departments", __name__, url_prefix="/api")  

class DepartmentAPI(MethodView):
    init_every_request = False
    
    def get(self):
        return [i.to_dict() for i in Department.query.all()]
    
    @validate()
    def post(self, body):
        pass

# Routes 
bp.add_url_rule("/departments", view_func=DepartmentAPI.as_view("deps_api"))