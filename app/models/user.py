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
    phone_number = db.Column(db.Text(), nullable=True)
    business_name = db.Column(db.Text(), nullable=True)
    
    password_hash = db.Column(db.String(128))
    events = db.relationship("Event", backref="user", lazy="dynamic")
    flower_templates = db.relationship("FlowerTemplate", backref="user", lazy="dynamic")
    admin = db.Column(db.Boolean, default=False, nullable=False)
    stripe_product_id = db.Column(db.String(256), nullable=True)
    stripe_subscription_id = db.Column(db.String(256), nullable=True)
    stripe_customer_id = db.Column(db.String(256), nullable=True)

    def set_last_login_time(self, time_iso_str=None):
        if time_iso_str:
            self.last_login_time = datetime.datetime.strptime(
                time_iso_str, "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        else:
            self.last_login_time = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()
        

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.add(self)
        db.session.commit()

    def set_username(self, username):
        if type(username) is not str:
            return
        if len([user for user in User.query.all() if user.username == username]) != 0:
            return
        self.username = username
        db.session.add(self)
        db.session.commit()

    def set_admin(self, admin):
        self.admin = admin
        db.session.add(self)
        db.session.commit()

    def set_email(self, email):
        self.email = email
        db.session.add(self)
        db.session.commit()
    
    def set_phone_number(self, phone_number):
        self.phone_number = phone_number
        db.session.add(self)
        db.session.commit()

    def set_business_name(self, business_name):
        self.business_name = business_name
        db.session.add(self)
        db.session.commit()

    def set_stripe_product_id(self, stripe_product_id):
        self.stripe_product_id = stripe_product_id
        db.session.add(self)
        db.session.commit()

    def set_stripe_subscription_id(self, stripe_subscription_id):
        self.stripe_subscription_id = stripe_subscription_id
        db.session.add(self)
        db.session.commit()

    def set_stripe_customer_id(self, stripe_customer_id):
        self.stripe_customer_id = stripe_customer_id
        db.session.add(self)
        db.session.commit()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_subscription_access(self):
        if self.admin:
            return True

        if self.stripe_subscription_id and self.stripe_customer_id:
            return True
        
        if self.stripe_subscription_id == "all_access":
            return True

        return False

    def has_stripe_subscription(self):
        return self.stripe_subscription_id and self.stripe_customer_id and self.stripe_subscription_id != "all_access"

    def delete(self):
        for x in self.events:
            x.delete()
        for x in self.flower_templates:
            x.delete()
        db.session.delete(self)
        db.session.commit()

    # Note: these tokens are cache'd on the front end and expired separately
    # this expiration is just a fallback to prevent keys from floating around indefinitely
    def generate_auth_token(self, expiration=3600):
        s = Serializer(app.config["SECRET_KEY"], expires_in=expiration)
        return s.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data["id"])
        return user

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "phone-number" : self.phone_number,
            "business-name" : self.business_name,
            "events": [e.id for e in self.events],
        }

    def to_json_full(self):
        full_json = self.to_json()
        full_json["admin"] = self.admin
        full_json["creation-time"] = self.creation_time
        full_json["last-login-time"] = self.last_login_time
        full_json["stripe-product-id"] = self.stripe_product_id
        full_json["stripe-subscription-id"] = self.stripe_subscription_id
        full_json["stripe-customer-id"] = self.stripe_customer_id
        return full_json

    @property
    def debug_log(self):
        return f"username: {self.username} - id: {self.id}"

    @staticmethod
    def make_user(
        username,
        password,
        email,
        admin=False,
        stripe_customer_id=None,
        stripe_product_id=None,
        stripe_subscription_id=None,
    ):
        username = username.strip()
        email = email.strip()
        password = password.strip()
        u = User(
            username=username,
            email=email,
            admin=admin,
            stripe_customer_id=stripe_customer_id,
            stripe_product_id=stripe_product_id,
            stripe_subscription_id=stripe_subscription_id,
        )
        u.set_password(password)
        return u

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def __repr__(self):
        return "<User {}>".format(self.username)
