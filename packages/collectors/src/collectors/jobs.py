from __future__ import annotations

import argparse
from datetime import date

from .finnhub import sync_daily_prices
from .materializer import materialize_daily_fundamentals
from .sec import sync_sec_filings, sync_sec_symbols


def main() -> None:
    parser = argparse.ArgumentParser(description='Collectors job runner')
    sub = parser.add_subparsers(dest='job', required=True)

    sec_parser = sub.add_parser('sync-sec-symbols')
    sec_parser.add_argument('--no-sic-enrichment', action='store_true')
    sec_parser.add_argument('--sic-limit', type=int, default=200)

    filings_parser = sub.add_parser('sync-filings')
    filings_parser.add_argument('--max-symbols', type=int, default=100)

    sub.add_parser('sync-prices')

    materializer_parser = sub.add_parser('materialize-fundamentals')
    materializer_parser.add_argument('--as-of-date', required=True, help='YYYY-MM-DD')

    args = parser.parse_args()

    if args.job == 'sync-sec-symbols':
        sync_sec_symbols(enrich_sic=not args.no_sic_enrichment, sic_enrichment_limit=args.sic_limit)
    elif args.job == 'sync-filings':
        sync_sec_filings(max_symbols=args.max_symbols)
    elif args.job == 'sync-prices':
        sync_daily_prices()
    elif args.job == 'materialize-fundamentals':
        materialize_daily_fundamentals(date.fromisoformat(args.as_of_date))


if __name__ == '__main__':
    main()
