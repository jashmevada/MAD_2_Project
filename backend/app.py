import logging
import flask
from flask.logging import default_handler
from flask_cors import CORS
from logging.config import dictConfig
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .utils.init_db import create_initial_data
from .utils.common import cache
from .controllers import subject, auth, instructors, chapters, students, quiz,departments
from .config import LocalDevelopmentConfig
from .utils.db import db,celery

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
# socketio.init_app(app)

celery.conf.update(
    broker_url= app.config["CELERY_BROKER_URL"],
    result_backend=app.config['CELERY_RESULT_BACKEND'],
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    worker_hijack_root_logger=False,
    broker_connection_retry_on_startup=True,
    worker_log_format="[%(asctime)s] [%(levelname)s] [%(task_name)s] [%(filename)s:%(lineno)d] - %(message)s",
    task_annotations={"tasks.add": {"rate_limit": "10/s"}},
)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# app.extensions["celery"] = celery

app.register_blueprint(auth.bp)
app.register_blueprint(instructors.bp)
app.register_blueprint(subject.bp)
app.register_blueprint(chapters.bp)
app.register_blueprint(students.bp)
app.register_blueprint(quiz.bp)
app.register_blueprint(departments.bp)
if __name__ == "__main__":
    app.run(debug=True)
