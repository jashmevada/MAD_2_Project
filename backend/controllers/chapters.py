from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flask_pydantic import validate
from flask.views import MethodView

from backend.utils.db import db
from ..models.schema import ChapterModel
from backend.utils.common import add_db, do_commit, cache
from ..models.model import Subject, Chapter

bp = Blueprint("chapters", __name__, url_prefix="/api")


class ChaptersAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]

    @cache.cached(timeout=30)
    def get(self):
        return [i.to_dict() for i in Chapter.query.all()]

    @validate()
    def post(self, body: ChapterModel):
        chapters = Chapter(
            name=body.name, description=body.description, subject_id=body.subject_id
        )
        print(chapters)
        return add_db([chapters], "Sucess", "Failed")

    def delete(self):
        chapter_id: int = request.args.get("id")
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        return do_commit("Chapter deleted successfully", "Chapter could not be deleted")

class SingleChapterAPI(MethodView):
    init_every_request = False
    decorators = [jwt_required()]

    def get(self, id):
        sub: Subject | None = Subject.query.get_or_404(id)
        return [i.to_dict() for i in sub.chapters]

    @validate()
    def post(self, id, body: ChapterModel):
        sub: Subject | None = Subject.query.get_or_404(id)
        chapters = Chapter(
            name=body.name, description=body.description
        )
        sub.chapters.append(chapters)
        return do_commit("Sucess", "Failed")

@validate()
@jwt_required()
def update_chapter(id: int, body: ChapterModel):
    chapter: Chapter = Chapter.query.get_or_404(id)
        
    chapter.description = body.description
    chapter.name = body.name
        
    return do_commit()

bp.add_url_rule("/chapters", view_func=ChaptersAPI.as_view("chapters_api"))
bp.route("/chapters/<int:id>", methods=['PUT'])(update_chapter)
bp.add_url_rule("/subjects/<int:id>/chapters", view_func=SingleChapterAPI.as_view("SingleChapterAPI"))