from app import db
from flask import render_template

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    symbol = db.Column(db.UnicodeText(), nullable=False)
    
    def repr_card(self):
        return render_template('models/company/card.html', company=self)

    @staticmethod
    def repr_card_grid(companies):
        return render_template('models/company/card_grid.html', companies=companies)

    @staticmethod
    def make(symbol):
        return Company(symbol=symbol)
