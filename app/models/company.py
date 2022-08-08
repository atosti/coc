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

    def refresh_latest_snapshot(self):
        latest_snapshot = (
                Snapshot.query.filter_by(company_id=self.id)
                .order_by(Snapshot.creation_time.desc())
                .first()
                )
        if latest_snapshot and not latest_snapshot.stale():
            return self

        snapshot = Snapshot.make(self.symbol, self)
        if snapshot:
            db.session.add(snapshot)
            db.session.commit()
        else:
            db.session.rollback()

        return self

    def latest_snapshot(self):
        latest_snapshot = (
                Snapshot.query.filter_by(company_id=self.id)
                .order_by(Snapshot.creation_time.desc())
                .first()
                )
        return latest_snapshot
    
    def latest_score(self):
        latest_snapshot = (
                Snapshot.query.filter_by(company_id=self.id)
                .order_by(Snapshot.creation_time.desc())
                .first())

        if latest_snapshot:
            return latest_snapshot.evaluate().score
        return -1

    def repr_dict(self):
        snapshot = (
            Snapshot.query.filter_by(company_id=self.id)
            .order_by(Snapshot.creation_time.desc())
            .first()
        )
        return {"symbol" : self.symbol,
                "snapshot" : snapshot.repr_dict()}

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

    def repr_company_card(self, in_dashboard):
        snapshot = (
            Snapshot.query.filter_by(company_id=self.id)
            .order_by(Snapshot.creation_time.desc())
            .first()
        )
        return render_template(
            "models/company/company_card.html",
            company=self,
            snapshot=snapshot,
            evaluation=snapshot.evaluate(),
            in_dashboard=in_dashboard
        )

    def repr_chart(self):
        snapshots = (
            Snapshot.query.filter_by(company_id=self.id)
            .order_by(Snapshot.creation_time.asc())
            .all()
        )

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

    def repr_company_table_tr(self):
        latest_snapshot = (
            Snapshot.query.filter_by(company_id=self.id)
            .order_by(Snapshot.creation_time.desc())
            .first()
        )
        return render_template(
                "models/company/company_table_tr.html", 
                company=self, 
                evaluation=latest_snapshot.evaluate(),
                snapshot=latest_snapshot)

    @staticmethod
    def make(symbol):
        return Company(symbol=symbol)
