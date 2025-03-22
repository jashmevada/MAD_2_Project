from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate
from flask.views import MethodView

from ..models.model import Instructor, Quiz, Question
from backend.models.schema import QuizCreateModel, UserModel
from backend.utils.common import add_db

bp = Blueprint("quiz", __name__, url_prefix="/api")


class QuizAPI(MethodView):
    init_every_request = False

    def get(self):
        return [i.to_dict() for i in Quiz.query.all()], 200

    @validate()
    def post(self, body: QuizCreateModel):
        quiz = Quiz(**body.model_dump(exclude=["questions"]))

        for question in body.questions:
            quiz.questions.append(Question(**question.model_dump()))

        print(quiz)
        return add_db([quiz], "Sucess", "Failed")
        # return {"message": "Quiz created successfully"}, 201


bp.add_url_rule("/quizzes", view_func=QuizAPI.as_view("quiz_api"))

