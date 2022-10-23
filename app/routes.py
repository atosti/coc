from app import app, db
from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user, login_user, logout_user, login_required
from app.models.list import List
from app.models.company import Company
from app.models.snapshot import Snapshot
from app.models.snapshot_failure import SnapshotFailure
import datetime
from dateutil import parser
from app.models.user import User
import json


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return render_template("login.html")
        login_user(user, password)
        user.set_last_login_time()
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("dashboard"))

    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/dashboard", methods=["GET", "POST", "DELETE", "PUT"])
@login_required
def dashboard():
    if request.method == "POST":
        _list = current_user.lists.first()
        if not _list:
            _list = List.make(current_user)
            db.session.add(_list)
            db.session.flush()

        symbol = request.form.to_dict().get("symbol")
        if symbol:
            symbol=symbol.upper()

        # TODO: check if valid symbol here, capitalization too
        company = Company.query.filter_by(symbol=symbol).first()
        if not company:
            company = Company.make(symbol)
            db.session.add(company)
            db.session.flush()

        _list.add_company(company)

        snapshot = (
            Snapshot.query.filter_by(company_id=company.id)
            .order_by(Snapshot.creation_time.desc())
            .first()
        )
        if not snapshot:
            snapshot = Snapshot.make(symbol, company)
            if snapshot:
                db.session.add(snapshot)
                db.session.commit()
            else:
                db.session.rollback()

        db.session.commit()
        companies = []
        if _list:
            companies = _list.companies()
        return Company.repr_card_grid(_list.companies())

    if request.method == "DELETE":
        target = request.form.get("target")

        _list = current_user.lists.first()
        if not _list:
            return ""  # should not happen

        company = Company.query.filter_by(id=target).first()
        _list.remove_company(company)
        db.session.commit()
        return ""

    if request.method == "PUT":
        target = request.form.get("target")
        company = Company.query.filter_by(id=target).first()
        if not company:
            return ""
        company = company.refresh_latest_snapshot()

        return company.repr_card()

    _list = current_user.lists.first()
    if not _list:
        _list = List.make(current_user)
        db.session.add(_list)
        db.session.commit()
    card_grid = Company.repr_card_grid(_list.companies())
    return render_template("dashboard.html", card_grid=card_grid)

@app.route("/market")
def market():
    current_sevens = [x for x in Company.query.all() if x.latest_score == 7]
    constant_sevens = []
    rising_sevens = []

    target_date = request.args.get('target_date')
    try:
        d = parser.parse(target_date)
        target_day = d.day
        target_month = d.month
        target_year = d.year
    except:
        now = datetime.datetime.today()
        target_day = 1
        if now.month == 1 :
            target_month = 11
            target_year = now.year - 1
        elif now.month == 2 :
            target_month = 12
            target_year = now.year - 1
        elif now.month == 3 :
            target_month = 1
            target_year = now.year
        else:
            target_month = now.month - 2
            target_year = now.year

    target_date = datetime.date(target_year, target_month, target_day)
    target_datetime = datetime.datetime(target_date.year, target_date.month, target_date.day)
    for company in current_sevens:
        target_snapshot = company.snapshot_at_time( target_datetime )
        if target_snapshot and target_snapshot.score() == 7:
            constant_sevens.append(company)
        elif target_snapshot and target_snapshot.score() != 7:
            rising_sevens.append(company)
        else:
            rising_sevens.append(company)

    constant_sevens_card_grid = Company.repr_card_grid_company_card(constant_sevens)
    rising_sevens_card_grid = Company.repr_card_grid_company_card(rising_sevens)

    return render_template("market.html", rising_sevens_card_grid=rising_sevens_card_grid, constant_sevens_card_grid=constant_sevens_card_grid, target_date=target_date)

@app.route("/company", methods=["GET"])
@login_required
def company_all():
    query = Company.query

    order_by = request.args.get('order_by', 'desc')
    if order_by == 'asc':
        query = query.order_by(Company.symbol.asc())
    else:
        query = query.order_by(Company.symbol.desc())

    companies = query.all()

    filter_by_score = request.args.get('score')
    if filter_by_score and filter_by_score in ['0','1','2','3','4','5','6','7']:
        filter_by_score_int = int(filter_by_score)
        companies = [x for x in companies if x.latest_score == filter_by_score_int]
    return render_template("companies.html", companies=companies)

@app.route("/company/<int:id>", methods=["GET"])
@login_required
def company(id):
    target = Company.query.filter_by(id=id).first()
    if not target:
        abort(404)

    in_dashboard = False
    _list = current_user.lists.first()
    if _list:
        in_dashboard = target in _list.companies()

    return render_template("models/company/company.html", target=target, in_dashboard=in_dashboard)

@app.route("/dashboard/company/<int:id>", methods=["POST"])
@login_required
def dashboard_company(id):
    target = Company.query.filter_by(id=id).first()
    if not target:
        abort(404)

    _list = current_user.lists.first()
    if not _list:
        _list = List.make(current_user)
        db.session.add(_list)
        db.session.flush()
    _list.add_company(target)
    db.session.add(_list)
    db.session.commit()
    return redirect(f"/company/{id}")

@app.route("/api/v1/company/<string:symbol>", methods=["GET"])
def api_company(symbol):
    auth_header = request.headers.get("Authorization", "").split(" ")
    if len(auth_header) != 2:
        abort(403)
    bearer = auth_header[0]
    token = auth_header[1]


    if not bearer  == "Bearer":
        abort(403)

    if token not in app.config["API_BEARER_TOKENS"]:
        abort(403)

    if request.method == "GET":
        company = Company.query.filter_by(symbol=symbol).first()
        if not company:
            company = Company.make(symbol)
            db.session.add(company)
            db.session.flush()
        if not company:
            return json.dumps({})

        company = company.refresh_latest_snapshot()
        return json.dumps({"company" : company.repr_dict()})

if __name__ == "__main__":
    app.run()
