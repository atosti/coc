from app import db
from app.models.snapshot import Snapshot
from flask import render_template


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    symbol = db.Column(db.UnicodeText(), nullable=False)

    def uri(self):
        return f"/company/{self.id}"

    def repr_card(self):
        snapshot = (
            Snapshot.query.filter_by(company_id=self.id)
            .order_by(Snapshot.creation_time.desc())
            .first()
        )
        return render_template(
            "models/company/card.html",
            company=self,
            snapshot=snapshot,
            evaluation=snapshot.evaluate(),
        )

    def repr_chart(self):
        snapshots = (
            Snapshot.query.filter_by(company_id=self.id)
            .order_by(Snapshot.creation_time.asc())
            .all()
        )

        _graham_numbers = []
        for s in snapshots:
            _graham_numbers.append(s.evaluate().graham_num)
        _max_graham_number = max(_graham_numbers)
        graham_number_scale = _max_graham_number * 1.10

        x = ""
        previous_score = None
        for snapshot in snapshots:
            x = x + snapshot.repr_tr_chart_score(previous_score=previous_score)
            _evaluation = snapshot.evaluate()
            previous_score = _evaluation.score
        return x

    @staticmethod
    def repr_card_grid(companies):
        return render_template("models/company/card_grid.html", companies=companies)

    @staticmethod
    def make(symbol):
        return Company(symbol=symbol)
