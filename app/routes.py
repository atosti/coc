from app import app, db
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.models.list import List 
from app.models.company import Company
from app.models.snapshot import Snapshot
from app.models.user import User 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return  render_template("login.html")
        login_user(user, password)
        user.set_last_login_time()
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("dashboard"))

    return redirect(url_for("dashboard"))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard', methods = ['GET','POST'])
@login_required
def dashboard():
    if request.method == "POST":

        _list = current_user.lists.first()
        if not _list:
            _list = List.make(current_user)
            db.session.flush()

        symbol = request.form.to_dict().get('symbol')
        # TODO: check if valid symbol here, capitalization too
        company = Company.query.filter_by(symbol=symbol).first()
        if not company:
            company = Company.make(symbol)
            db.session.add(company)
            db.session.flush()

        _list.add_company(company)

        snapshot = Snapshot.query.filter_by(company_id=company.id).order_by(Snapshot.creation_time.desc()).first()
        if not snapshot:
            snapshot = Snapshot.make(symbol, company)
            if snapshot:
                db.session.add(snapshot)
                db.session.commit()
            else:
                db.session.rollback()

        # db.session.add(_list)
        db.session.commit()
        return Company.repr_card_grid(_list.companies())

    _list = current_user.lists.first()
    card_grid = Company.repr_card_grid(_list.companies())
    return render_template('dashboard.html', card_grid=card_grid)


if __name__ == '__main__':
   app.run()
