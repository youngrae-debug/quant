from __future__ import annotations

import argparse
from datetime import date, datetime

from .batch_jobs import refresh_recommendations, run_quant_scoring


def _today() -> date:
    return datetime.utcnow().date()


def main() -> None:
    parser = argparse.ArgumentParser(description='API batch jobs')
    sub = parser.add_subparsers(dest='job', required=True)

    scoring = sub.add_parser('score')
    scoring.add_argument('--as-of-date', default=None, help='YYYY-MM-DD (default: today UTC)')

    refresh = sub.add_parser('refresh-recommendations')
    refresh.add_argument('--as-of-date', default=None, help='YYYY-MM-DD (default: today UTC)')

    args = parser.parse_args()

    as_of = date.fromisoformat(args.as_of_date) if args.as_of_date else _today()

    if args.job == 'score':
        run_quant_scoring(as_of)
    elif args.job == 'refresh-recommendations':
        refresh_recommendations(as_of)


if __name__ == '__main__':
    main()
