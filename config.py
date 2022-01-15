import os

basedir = os.path.abspath(os.path.dirname(__file__))
import json
from loguru import logger


class Config(object):

    ENV = os.environ.get("ENV") or "development"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "A DUMMY SECRET KEY GOES HERE"

    HEROKU_RELEASE_VERSION = os.getenv("HEROKU_RELEASE_VERSION", "")

    uri = os.getenv("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri or "sqlite:///" + os.path.join(basedir, "app.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
