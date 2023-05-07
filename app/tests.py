import json
from pathlib import Path

import pytest

from osm_query import OverpassClient
from tile_cache import TileCache


class TestJson:
    @pytest.fixture
    def tile_cache(self):
        return TileCache(
            Path("_tile_cache"),
            max_days=7,
            max_entries=1e5,
            overpass_client=OverpassClient(
                "https://overpass.kumi.systems/api/interpreter/", "Overscape/0.1"
            ),
        )

    def test_json_schema(self, tile_cache):
        """Check that we match the Soundscape GeoJSON format described at
        https://github.com/steinbro/soundscape/blob/main/docs/services/data-plane-schema.md

        This might be checkable with jsonschema validation.
        """
        json_data = tile_cache.get(18741, 25054)
        #with open("../reference/18747_25074.json") as f:
        #    json_data = json.load(f)

        assert len(json_data.keys()) == 2
        assert json_data["type"] == "FeatureCollection"
        for feature in json_data["features"]:
            assert "feature_type" in feature
            assert "feature_value" in feature
            assert "geometry" in feature
            assert "osm_ids" in feature
            assert "properties" in feature
            assert "type" in feature

            assert "coordinates" in feature["geometry"]
            assert "type" in feature["geometry"]
