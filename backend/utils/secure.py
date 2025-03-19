from flask_security import Security, SQLAlchemyUserDatastore


from .db import db
from ..models.model import User

# __datastore = SQLAlchemyUserDatastore(db, Role, User)
# security = Security(datastore=__datastore, register_blueprint=True)
