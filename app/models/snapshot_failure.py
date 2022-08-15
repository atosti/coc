from app import db
from flask import render_template
from app.models.company import Company
from backend.core import handler
from backend.core import company as backend_company

from app.models.utils import JSONEncodedDict
import datetime


class SnapshotFailure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    symbol = db.Column(db.UnicodeText(), nullable=False)
    

    @staticmethod
    def make(symbol):
        return SnapshotFailure(symbol=symbol)
