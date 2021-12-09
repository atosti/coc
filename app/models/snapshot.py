from app import db
from flask import render_template
from backend.core import handler
from backend.core import company as backend_company

from sqlalchemy.types import TypeDecorator, VARCHAR
import json
import datetime


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    data = db.Column(JSONEncodedDict)

    def evaluate(self):
        return backend_company.Company(self.data.get('symbol'), self.data)

    @staticmethod
    def make(symbol, company):
        print(company.id)
        _handler_company, parsed_data, scrape_data = handler.check_and_return_output(symbol, ['j', 's'])
        if scrape_data:
            return Snapshot(company_id=company.id, data=scrape_data)


