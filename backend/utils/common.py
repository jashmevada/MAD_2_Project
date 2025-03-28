from flask_caching import Cache
from backend.utils.db import db

# Use this to add a single record to the database
def add_db(models, msg: str | dict = "Success", err_msg: str | dict = "Error"):
    try:
        db.session.add_all(models)
        db.session.commit()
        return {"message": msg}, 200
    except Exception as e:
        db.session.rollback()
        # raise e
        return {"message": err_msg, "error": f"{e}"}, 500

# Use this to update/add multiple records in the database
def add_batch_db(models, msg: str | dict = "Success", err_msg: str | dict = "Error"):
    try:
        db.session.add_all(models)
        db.session.commit()
        return {"message": msg}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": err_msg, "error": f"{e}"}, 500


def do_commit(msg: str | dict = "Success", err_msg: str | dict = "Error"):
    try:
        db.session.commit()
        return {"message": msg}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": err_msg, "error": f"{e}"}, 500
    
    
cache = Cache()
