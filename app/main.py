import argparse
from pathlib import Path
from server import run_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overpass-url",
        help="URL of Overpass API server",
        default="https://overpass.kumi.systems/api/interpreter/",
        # defauult="http://overpass-api.de/api/interpreter",
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
    args = parser.parse_args()

    run_server(
        args.overpass_url,
        args.user_agent,
        args.cache_dir,
        args.cache_days,
        args.cache_size,
    )
