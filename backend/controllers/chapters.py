from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from ..models.schema import ChapterModel, SubjectCreate
from backend.utils.common import add_db, do_commit
from ..models.model import Subject, Chapter, Instructor, Student, User

bp = Blueprint("chapters", __name__, url_prefix="/api")


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
        return add_db([chapters], "Sucess", "Failed")


class SingleChapterAPI(MethodView):
    init_every_request = False

    def get(self, id):
        sub: Subject | None = Subject.query.get_or_404(id)
        return [i.to_dict() for i in sub.chapters]

    @validate()
    def post(self, id, body: ChapterModel):
        sub: Subject | None = Subject.query.get_or_404(id)
        chapters = Chapter(
            name=body.title, description=body.description
        )
        print(chapters)
        sub.chapters.append(chapters)
        return do_commit("Sucess", "Failed")

    def patch(self, id):
        pass

bp.add_url_rule("/chapters", view_func=ChaptersAPI.as_view("chapters_api"))
bp.add_url_rule("/subjects/<int:id>/chapters", view_func=SingleChapterAPI.as_view("SingleChapterAPI"))
