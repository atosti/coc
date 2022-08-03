from app import app, db
from app.models.snapshot import Snapshot
from app.models.company import Company
from app.models.user import User
from app.models.utils import all_nyse_symbols
from datetime import datetime, timedelta
from loguru import logger
import argparse, random


def log_results(out, args):
    if not out:
        return

    logger.info(out)
    # if args.output_email:
    #     t = None
    #     h = None
    #     with app.app_context():
    #         t = render_template("email/tasks_referrals.txt", job=out)
    #         h = render_template("email/tasks_referrals.html", job=out)
    #     send_email(
    #         subject=f"{app.config.get('DOMAIN_URL')} - job {out.get('name')} completed at {out.get('completed-at')}",
    #         sender=app.config["MAIL_ADMINS"][0],
    #         recipients=app.config["MAIL_ADMINS"],
    #         text_body=t,
    #         html_body=h,
    #     )

def snapshot_create(symbol: str):
    return


def snapshots_refresh(limit: int = 5, days: int = 7):
    symbols = all_nyse_symbols()
    subset = []
    for symbol in symbols:
        # Find or Populate Companies from list
        company = Company.query.filter_by(symbol=symbol).first()
        if not company:
            company = Company.make(symbol)
            db.session.add(company)
            db.session.flush()
        # Check for latest snapshot
        latest_snapshot = (
            Snapshot.query.filter_by(company_id=company.id)
            .order_by(Snapshot.creation_time.desc())
            .first()
        )
        if not latest_snapshot or latest_snapshot.stale(days):
            subset.append(company)
        if len(subset) >= limit:
            break
    for company in subset:
        logger.info(f"Refreshing snapshot for {company.symbol}.")
        company.refresh_latest_snapshot()
    return [company.symbol for company in subset] # Returns a list of which symbols were updated

def snapshots_known():
    outputs = []
    errors = []

    companies = Company.query.all()
    for company in companies:
        try:
            snapshot = Snapshot.make(company.symbol, company)
            db.session.add(snapshot)
            db.session.commit()
            outputs.append({"message": f"fetched snapshot for {company.symbol}"})
        except:
            errors.append({"message": f"failed to fetch snapshot for {company.symbol}"})
    return {
        "name": "snapshot:known",
        "completed-at": str(datetime.now()),
        "args": args,
        "errors": errors,
        "successes": outputs,
    }

def user_reset_password(username, password):

    outputs = []
    errors = []

    # print(User.query.all())

    user = User.query.filter_by(username=username).first()
    if user:
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        outputs.append({"message": f"updated password for user {username}"})
    else:
        errors.append({"message": f"failed to fetch a user with username {username}"})
        
    return {
            "name": "user:reset-password",
            "completed-at": str(datetime.now()),
            "args": args,
            "errors": errors,
            "successes": outputs,
    }


def main(args, task):
    if task == "snapshots:known":
        out = snapshots_known()
        log_results(out, args)
        return out
    if task == "user:reset-password":
        if not args.username:
            logger.warning("--username is a required argument.")
            return

        if not args.password:
            logger.warning("--password is a required argument.")
            return

        out = user_reset_password(args.username, args.password)
        log_results(out, args)
        return out
    if task == "snapshots:refresh":
        out = snapshots_refresh()
        log_results(out, args)
        return out


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--task",
        type=str,
        help="Execution mode (options: snapshots:known).",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        help="target username",
    )
    parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="new password",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = process_args()
    main(args, args.task)


