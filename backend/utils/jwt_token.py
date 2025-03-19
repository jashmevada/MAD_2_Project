import jwt
from ..models.model import User


class JWTAuth:
    def __init__(self) -> None: ...

    def __create_token(user: User): ...
