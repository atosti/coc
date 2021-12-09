from app import db
from flask import render_template

class Snapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creation_time = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    
    def __init__(self, symbol):
        self.symbol = symbol
    
    def repr_card(self):
        return render_template('models/company/card.html', company=self)
        
