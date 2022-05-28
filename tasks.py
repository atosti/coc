from app import app, db
from app.models.snapshot import Snapshot
from app.models.company import Company
from datetime import datetime, timedelta
from loguru import logger
import argparse


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


def main(args, task):
    if task == "snapshots:known":
        out = snapshots_known()
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
    return parser.parse_args()


if __name__ == "__main__":
    args = process_args()
    main(args, args.task)


