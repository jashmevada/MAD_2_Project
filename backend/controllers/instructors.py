from flask import Blueprint, app, current_app, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from ..models.model import Instructor, Student, User
from backend.models.schema import UserLogin, UserModel
from backend.utils.common import add_db

bp = Blueprint("instructors", __name__, url_prefix="/api/instructors")


class InstructorsAPI(MethodView):
    init_every_request = False

    def get(self):
        approval_arg: bool | None = request.args.get("approval")
        if approval_arg:
            match approval_arg:
                case True:
                    return [
                        i.to_dict()
                        for i in Instructor.query.filter_by(approval=False).all()
                    ]
        return [i.to_dict() for i in Instructor.query.all()], 200

    def patch(self):
        pass

@bp.route("/<int:id>/status", methods=['PATCH'])
def update_status(id: int):
    approval: bool = request.args.get("approval")
    
    instructor: Instructor = Instructor.query.get_or_404(id)
    
    if approval or approval == "true" or approval == "false":
        instructor.approval = True if approval == "true" else False  
        return add_db([instructor], "Success Update", "Failed to update")

    return {"msg": "Error"}, 400 

bp.add_url_rule("/", view_func=InstructorsAPI.as_view("instructors_api"))
