import argparse
import logging
from pathlib import Path
from server import run_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overpass-url",
        help="URL of Overpass API server",
        default="https://overpass.kumi.systems/api/interpreter/",
        # default="http://overpass-api.de/api/interpreter",
    )
    parser.add_argument(
        "--user-agent",
        help="How to identify this script to the Overpass server being queried",
        default="Overscape/0.1 (https://github.com/openscape-community/overscape-server)",
    )
    parser.add_argument(
        "--cache-days",
        type=int,
        help="Number of days after which cached items should be refreshed",
        default=7,
    )
    parser.add_argument(
        "--cache-dir",
        type=int,
        help="Directory to store cached JSON responses",
        default=Path("_tile_cache"),
    )
    parser.add_argument(
        "--cache-size",
        type=int,
        help="Maximum number of JSON responses to store",
        default=1e5,
    )
    parser.add_argument("--port", type=int, help="TCP Port to listen on", default=8080)
    # To get a sentry dsn, create a project either on your hosted sentry instance, or sentry.io and choose python as the platform.
    # If you already have a project created in Sentry, navigate to it, then go to client keys (dsn) in the menu.
    parser.add_argument(
        "--sentry-dsn",
        type=str,
        help="""The sentry data source name URL to pass to the SDK. If none is provided, sentry is not used.""",
    )
    parser.add_argument(
        "--sentry-tsr",
        type=float,
        help="""The trace sample rate value for overscape in sentry, a number from 0.0 to 1.0, which sets the approximate percent of app queries will have traces recorded for sampling.""",
        default=0.1,
    )
    levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument("--log-level",
        choices=levels,
        default="INFO",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    run_server(
        args.overpass_url,
        args.user_agent,
        args.cache_dir,
        args.cache_days,
        args.cache_size,
        args.port,
        args.sentry_dsn,
        args.sentry_tsr,
    )
