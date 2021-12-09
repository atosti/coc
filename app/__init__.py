from flask import Flask
from config import Config
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
def auto_constraint_name(constraint, table):
    if constraint.name is None or constraint.name == "_unnamed_":
        return "sa_autoname_%s" % str(uuid.uuid4())[0:5]
    else:
        return constraint.name

convention = {
    "auto_contstraint_name" : auto_constraint_name,
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s", #causes problems with test db creation, needs to be commented out when running tests
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)

migrate = Migrate(app, db, render_as_batch=True)
# login = LoginManager(app)
# login.login_view = "login"

from app import routes
