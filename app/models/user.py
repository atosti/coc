from app import app, db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import datetime
import sqlalchemy
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    last_login_time = db.Column(db.DateTime(timezone=True), nullable=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    lists = db.relationship("List", backref="user", lazy="dynamic")
    admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_last_login_time(self, time_iso_str=None):
        if time_iso_str:
            self.last_login_time = datetime.datetime.strptime(
                time_iso_str, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        else:
            self.last_login_time = datetime.datetime.now()
        db.session.add(self)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.add(self)

    def set_username(self, username):
        if type(username) is not str:
            return
        if User.query.filter_by(username=username).first():
            return
        self.username = username
        db.session.add(self)

    def set_admin(self, admin):
        self.admin = admin
        db.session.add(self)

    def set_email(self, email):
        self.email = email
        db.session.add(self)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def debug_log(self):
        return f"username: {self.username} - id: {self.id}"

    @staticmethod
    def make(username, password, email, admin=False):
        username = username.strip()
        email = email.strip()
        password = password.strip()
        u = User(username=username, email=email, admin=admin)
        u.set_password(password)
        return u

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def __repr__(self):
        return "<User {}>".format(self.username)
