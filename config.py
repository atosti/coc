import os

basedir = os.path.abspath(os.path.dirname(__file__))
import json
from loguru import logger

class Config(object):
    def _database_url(database_url):
        uri = os.getenv("DATABASE_URL")
        if uri and uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        return uri


    ENV = os.environ.get("ENV") or "development"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "A DUMMY SECRET KEY GOES HERE"
    
    HEROKU_RELEASE_VERSION = os.getenv("HEROKU_RELEASE_VERSION","")
    
    SQLALCHEMY_DATABASE_URI = _database_url(database_url) or "sqlite:///" + os.path.join(basedir, "app.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
