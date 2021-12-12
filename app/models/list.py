from app import db
from flask import render_template
from app.models.company import Company
from backend.core import handler
from backend.core import company as backend_company

from app.models.utils import JSONEncodedDict
import datetime

class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    data = db.Column(JSONEncodedDict) 

    def add_company(self, company):
        _company_list = []
        _company_list.extend(self.data)
        if not company.id in _company_list:
            _company_list.append(company.id)
            self.data = _company_list # These changes will not commit to the db unless the self.data object has been reassigned to a new object
            db.session.add(self)

    def remove_company(self, company):
        company_ids = []
        for x in self.data:
            if x != company.id:
                company_ids.append(x)
        self.data = company_ids
        db.session.add(self)

    def set_companies(self, companies):
        for company in companies:
            self.add_company(company)

    def companies(self):
        companies_by_id = {}
        for x in Company.query.filter(Company.id.in_(self.data)).all():
            companies_by_id[x.id] = x

        ordered_companies = []
        for company_id in self.data:
            ordered_companies.append(companies_by_id.get(company_id))
        return ordered_companies

    @staticmethod
    def make(user):
        return List(user_id=user.id, data=[])


