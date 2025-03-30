from celery import Celery, Task

def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.set_default()
    
    celery_app.conf.update( 
    broker_url= app.config["CELERY_BROKER_URL"],
    result_backend=app.config['CELERY_RESULT_BACKEND'],
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=False,
    worker_hijack_root_logger=False,
    broker_connection_retry_on_startup=True,
    worker_log_format="[%(asctime)s] [%(levelname)s] [%(task_name)s] [%(filename)s:%(lineno)d] - %(message)s",
    task_annotations={"tasks.add": {"rate_limit": "10/s"}},)
    
    app.extensions["celery"] = celery_app
   
    return celery_app
