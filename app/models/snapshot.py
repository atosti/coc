from datetime import datetime, timezone, timedelta
from app import db
from flask import render_template
from app.models.utils import JSONEncodedDict
from backend.core import handler
from backend.core import company as backend_company


class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    data = db.Column(JSONEncodedDict)

    def evaluate(self):
        return backend_company.Company(self.data.get("symbol"), self.data)

    def stale(self, days: int = 0):
        today = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        creation_date = datetime.strptime(self.creation_time.strftime("%Y-%m-%d"), "%Y-%m-%d")
        return abs((creation_date - today).days) > days

    def repr_dict(self):
        return self.data

    def repr_tr_chart_score(self, previous_score=None):
        return render_template(
            "models/snapshot/chart_tr_score.html",
            target=self,
            evaluation=self.evaluate(),
            previous_score=previous_score,
        )

    @staticmethod
    def make(symbol, company):
        _handler_company, parsed_data, scrape_data = handler.check_and_return_output(
            symbol, ["j", "s"]
        )
        if scrape_data:
            return Snapshot(company_id=company.id, data=scrape_data)
