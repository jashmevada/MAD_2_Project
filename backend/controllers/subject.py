from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_pydantic import validate
from flask.views import MethodView

from ..models.schema import SubjectCreate
from backend.utils.common import add_db, do_commit, cache
from ..models.model import Subject
from ..utils.db import db 

bp = Blueprint("subject", __name__, url_prefix="/api")  


class SubjectsAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]
    
    @cache.cached(timeout=30)
    def get(self):
        return [i.to_dict() for i in Subject.query.all()]

    @validate()
    def post(self, body: SubjectCreate):
        sub = Subject(**body.model_dump())
        cache.clear()
        return add_db([sub], "Sucess", "Failed")


class SingleSubjectAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]

    def get(self, id):
        return Subject.query.get_or_404(id).to_dict()
    
    @validate()
    def put(self, id, body: SubjectCreate):
        sub: Subject = Subject.query.get_or_404(id)
        sub.name = body.name
        sub.description = body.description
        return do_commit("Success", "Failed")
    
    
    def delete(self, id: int):
        sub: Subject = Subject.query.get_or_404(id)
        db.session.delete(sub)
        return do_commit("Success", "Error")


bp.add_url_rule("/subjects", view_func=SubjectsAPI.as_view("subjects_api"))
bp.add_url_rule("/subjects/<int:id>", view_func=SingleSubjectAPI.as_view("SingleSubjectAPI"))
