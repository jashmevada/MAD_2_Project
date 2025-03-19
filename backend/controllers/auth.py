from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_pydantic import validate

from backend.models.model import Instructor, Student, User
from backend.models.schema import UserLogin, UserModel
from backend.utils.common import add_db

bp = Blueprint("auth", __name__, url_prefix="/api")


@bp.route("/login", methods=["POST"])
@validate()
def login(body: UserLogin):
    user: User = User.query.filter_by(username=body.username).first()
    if user and user.password == body.password:
        access_token = create_access_token(
            identity=str(user.id), additional_claims={"role": user.role}
        )
        return jsonify(access_token=access_token, role=user.role, data=user.to_dict())
    return jsonify({"message": "Invalid credentials"}), 401


@bp.route("/register", methods=["POST"])
@validate()
def register(body: UserModel):
    # current_app.logger.info(user.to_dict())
    existing_user = User.query.filter(
        (User.username == body.username) | (User.email == body.email)
    ).first()

    if existing_user:
        return jsonify(
            {
                "success": False,
                "message": "Username or email already exists",
            }
        ), 400

    resp, code = "", 500
    if body.data.user_role == "instructor":
        instructor = Instructor(
            **body.data.model_dump(exclude="user_role"),
            role="instructor",
            username=body.username,
            email=body.email,
            password=body.password,
            approval=False,
        )
        resp, code = add_db([instructor])

    elif body.data.user_role == "student":
        student = Student(
            **body.data.model_dump(exclude="user_role"),
            role="student",
            username=body.username,
            email=body.email,
            password=body.password,
        )
        resp, code = add_db([student])
        current_app.logger.info(resp)

    if code == 200:
        return jsonify({"message": "User registered"}), 201

    return {"message": "Error"}, 500


@bp.route("/test")
@jwt_required()
def test():
    return jsonify({"d": "a"})
