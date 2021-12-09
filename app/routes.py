from app import app, db
from flask import render_template, request
from app.models.company import Company
from app.models.snapshot import Snapshot

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods = ['POST', 'GET'])
def dashboard():
    if request.method == "POST":
        symbol = request.form.to_dict().get('symbol')
        # TODO: check if valid symbol here
        company = Company.make(symbol)
        db.session.add(company)
        db.session.flush()
        snapshot = Snapshot.make(symbol, company)
        if snapshot:
            db.session.add(snapshot)
            db.session.commit()
        else:
            db.session.rollback()

        companies = Company.query.order_by(Company.creation_time).all()
        return Company.repr_card_grid(companies)

    companies = Company.query.order_by(Company.creation_time).all()
    card_grid = Company.repr_card_grid(companies)
    return render_template('dashboard.html', card_grid=card_grid)


if __name__ == '__main__':
   app.run()
