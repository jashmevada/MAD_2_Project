from functools import wraps
from flask import request
from flask_security import Security, SQLAlchemyUserDatastore, auth_required

# from backend.db import Base, db
# from backend.models.model import Role, User

__datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(datastore=__datastore, register_blueprint=True)

TOKEN_HEADER = "Auth-Token"

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if TOKEN_HEADER in request.headers:
#             token = request.headers[TOKEN_HEADER]
#             if not token:
#                 return {"status": "token_missing"}, 401
