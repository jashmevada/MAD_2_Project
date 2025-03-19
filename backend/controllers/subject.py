from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from backend.models.model import Instructor, Student, User
from ..models.schema import SubjectCreate
from backend.utils.common import add_db
from ..models.model import Subject

bp = Blueprint("subject", __name__, url_prefix="/api/")


class SubjectsAPI(MethodView):
    init_every_request = False

    def get(self):
        return [i.to_dict() for i in Subject.query.all()]

    @validate()
    def post(self, body: SubjectCreate):
        sub = Subject(**body.model_dump())
        print(sub)

        return add_db([sub], "Sucess", "Failed")


class SingleSubjectAPI(MethodView):
    init_every_request = False

    def get(self, id):
        return Subject.query.get_or_404(id).to_dict()

    def post(self, id):
        pass

    def patch(self, id):
        pass


@bp.route("subjects/<int:id>/chapters")
def chapters_per_subject(id: int):
    sub: Subject | None = Subject.query.get_or_404(id)
    return [i.to_dict() for i in sub.chapters]


bp.add_url_rule("subjects/", view_func=SubjectsAPI.as_view("subjects_api"))
bp.add_url_rule("/<int:id>", view_func=SingleSubjectAPI.as_view("SingleSubjectAPI"))
