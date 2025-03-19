class LocalDevelopmentConfig(object):
    DEBUG = True
    SECRET_KEY = "secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///test2.db"
    # ACME_CONFIG = "./acme.conf"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-secret-key'
