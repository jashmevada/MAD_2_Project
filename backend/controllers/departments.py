from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from ..models.schema import DepartmentModel
from ..utils.common import add_db, do_commit, cache
from ..models.model import Department, Subject
from ..utils.db import db 

bp = Blueprint("departments", __name__, url_prefix="/api")  

class DepartmentAPI(MethodView):
    init_every_request = False
    
    def get(self):
        return [i.to_dict() for i in Department.query.all()]
    
    @validate()
    def post(self, body: DepartmentModel):
        dep = Department(**body.model_dump())
        return add_db([dep], "Sucess", "Failed")
    
class SingleDepartmentAPI(MethodView):
    init_every_request = False 
    decorators = [jwt_required()]
    
    def get(self, id: int):
        return Department.query.get_or_404(id).to_dict()

    @validate()
    def put(self, id: int, body: DepartmentModel):
        dep: Department = Department.query.get_or_404(id) 
    
        dep.description = body.description
        dep.title = body.title 
        
        return do_commit()
    
    def delete(self, id: int):
        dep = Department.query.get_or_404(id)
        
        try:
            db.session.delete(dep)
            return do_commit()
        except Exception as e:
            return {'msg': f'Error {e}'}, 500

@jwt_required()
def get_subjects_by_department(id: int):
    dep: Department = Department.query.get_or_404(id)
    
    return [i.to_dict() for i in dep.subjects]

# Routes 
bp.add_url_rule("/departments", view_func=DepartmentAPI.as_view("deps_api"))
bp.add_url_rule("/departments/<int:id>", view_func=SingleDepartmentAPI.as_view("single_dep_api"))
bp.route("/departments/<int:id>/subjects")(get_subjects_by_department)