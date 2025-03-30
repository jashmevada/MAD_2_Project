import logging
import flask
from flask.logging import default_handler
from flask_cors import CORS
from logging.config import dictConfig
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .utils.init_db import create_initial_data
from .utils.common import cache
from .controllers import subject, auth, instructors, chapters, students, quiz,departments, analytics
from .config import LocalDevelopmentConfig
from .utils.db import db
from .utils.celery_init import celery_init_app
from .utils.mail import mail 

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

# Setup app

app = flask.Flask(__name__)
app.config.from_object(LocalDevelopmentConfig)

migrate = Migrate(app, db, render_as_batch=True)

CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    expose_headers="Authorization,Content-Type,Authentication-Token,XSRF-TOKEN",
)


for logger in (logging.getLogger(app.name), logging.getLogger("sqlalchemy")):
    logger.addHandler(default_handler)

    
db.init_app(app)

with app.app_context():
    db.create_all()
    create_initial_data()

JWTManager(app)
cache.init_app(app)
mail.init_app(app)

celery = celery_init_app(app)
celery.autodiscover_tasks()


app.register_blueprint(auth.bp)
app.register_blueprint(instructors.bp)
app.register_blueprint(subject.bp)
app.register_blueprint(chapters.bp)
app.register_blueprint(students.bp)
app.register_blueprint(quiz.bp)
app.register_blueprint(departments.bp)
app.register_blueprint(analytics.bp)

if __name__ == "__main__":
    app.run(debug=True)
