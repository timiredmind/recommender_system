from os import urandom
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://timileyin:goodness4321@localhost/recommender_system"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = urandom(12).hex()
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    RATELIMIT_HEADERS_ENABLED = True