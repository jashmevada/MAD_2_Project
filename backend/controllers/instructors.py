from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from backend.utils.common import add_db, do_commit

from ..models.model import Instructor

bp = Blueprint("instructors", __name__, url_prefix="/api")


class InstructorsAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]
    
    def get(self):
        approval_arg: bool | None = request.args.get("approval", type=bool)
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


class SingleInstructorAPI(MethodView):
    init_every_request = False 
    decorators = [jwt_required()]
    
    def get(self, id: int):
        return Instructor.query.get_or_404(id)

    def delete(self, id: int):
        pass
    
    
@jwt_required()
def update_status(id: int):
    approval: bool | None = request.args.get("approval", type=bool)
    
    instructor: Instructor = Instructor.query.get_or_404(id)
    
    if approval:
        instructor.approval = True if approval == "true" else False  
        return do_commit("Success Update", "Failed to update")

    return {"msg": "Error"}, 400 
    
    
# Routes
bp.add_url_rule("/instructors", view_func=InstructorsAPI.as_view("instructors_api"))
bp.add_url_rule("/instructors/<int:id>", view_func=SingleInstructorAPI.as_view("single_instructors_api"))
bp.route("/instructors/<int:id>/status", methods=['PATCH'])(update_status)