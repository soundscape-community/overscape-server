import gzip
import json
import random
from datetime import datetime, timedelta


class CompressedJSONCache:
    """Used both by the server to store GeoJSON responses, and also by the
    tests to store Overpass query results.
    """

    def __init__(self, dir, max_days, max_entries):
        self.dir = dir
        self.max_age = timedelta(days=max_days)
        self.max_entries = max_entries

        if not self.dir.exists():
            self.dir.mkdir()

    def evict_if_needed(self):
        # TODO better algorithm than random file
        entries = list(self.dir.iterdir())
        if len(entries) > self.max_entries:
            random.choice(entries).unlink()

    def _should_fetch(self, path):
        # remove cached file if not valid gzipped json
        if path.exists():
            try:
                with gzip.open(path, "rb") as f:
                    json.load(f)
            except (gzip.BadGzipFile, json.decoder.JSONDecodeError):
                path.unlink()

        return (
            not path.exists()
            or (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime))
            > self.max_age
        )

    async def get(self, key, fetch_func):
        path = self.dir.joinpath(f"{key}.json.gz")
        if self._should_fetch(path):
            self.evict_if_needed()
            data = await fetch_func()
            with gzip.open(path, "wt", encoding="ascii") as f:
                json.dump(data, f)

        with gzip.open(path, "rb") as f:
            return json.load(f)
