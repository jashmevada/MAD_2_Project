from backend.utils.db import db

def add_db(models, msg: str | dict = "Success", err_msg: str | dict = "Error"):
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