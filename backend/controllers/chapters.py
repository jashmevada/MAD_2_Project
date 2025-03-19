from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from ..models.schema import ChapterModel, SubjectCreate
from backend.utils.common import add_db
from ..models.model import Subject, Chapter, Instructor, Student, User

bp = Blueprint("chapters", __name__, url_prefix="/api/chapters")


class ChaptersAPI(MethodView):
    init_every_request = False

    def get(self):
        return [i.to_dict() for i in Chapter.query.all()]

    @validate()
    def post(self, body: ChapterModel):
        chapters = Chapter(
            name=body.name, description=body.description, subject_id=body.subject_id
        )
        print(chapters)
        return {"message": "done"}, 200


class SingleChapterAPI(MethodView):
    init_every_request = False

    def get(self, id):
        return Chapter.query.get_or_404(id).to_dict()

    def post(self, id):
        pass

    def patch(self, id):
        pass


bp.add_url_rule("/", view_func=ChaptersAPI.as_view("chapters_api"))
bp.add_url_rule("/", view_func=SingleChapterAPI.as_view("SingleChapterAPI"))
