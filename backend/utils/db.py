from flask_socketio import SocketIO
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
import redis

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

class Base(DeclarativeBase): 
    metadata = MetaData(naming_convention=naming_convention)


db = SQLAlchemy(model_class=Base)

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

socketio = SocketIO(cors_allowed_origins="*")