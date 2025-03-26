from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from backend.models.model import Instructor, Student, User
from ..models.schema import SubjectCreate
from backend.utils.common import add_db, do_commit, cache
from ..models.model import Subject

bp = Blueprint("subject", __name__, url_prefix="/api")  


class SubjectsAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]
    
    # @cache.cached(timeout=60)
    def get(self):
        return [i.to_dict() for i in Subject.query.all()]

    @validate()
    def post(self, body: SubjectCreate):
        sub = Subject(**body.model_dump())
        print(sub)
        return add_db([sub], "Sucess", "Failed")


class SingleSubjectAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]

    def get(self, id):
        return Subject.query.get_or_404(id).to_dict()

    def post(self, id):
        pass

    @validate()
    def put(self, id, body: SubjectCreate):
        sub: Subject = Subject.query.get_or_404(id)
        sub.name = body.name
        sub.description = body.description
        return do_commit("Sucess", "Failed")

    def patch(self, id):
        pass



bp.add_url_rule("/subjects", view_func=SubjectsAPI.as_view("subjects_api"))
bp.add_url_rule("/subjects/<int:id>", view_func=SingleSubjectAPI.as_view("SingleSubjectAPI"))
