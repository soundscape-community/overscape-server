import json
from pathlib import Path

import pytest

from overpass import OverpassClient, tile_bbox_from_x_y


class TestGeoJSON:
    @pytest.fixture
    def overpass_client(self):
        return OverpassClient(
            "https://overpass.kumi.systems/api/interpreter/",
            "Overscape/0.1",
            cache_dir=Path("_test_cache"),
            cache_days=7,
            cache_size=1e5,
        )

    @pytest.mark.parametrize('x,y', [
        [18741, 25054],
    ])
    def test_geojson_schema(self, x, y, overpass_client):
        """Check that we match the Soundscape GeoJSON format described at
        https://github.com/steinbro/soundscape/blob/main/docs/services/data-plane-schema.md

        This might be checkable with jsonschema validation.
        """
        # Outside of tests, we cache our transformed GeoJSON, but since
        # we want to test the transformation, we only cache the response
        # from Overpass.
        coords = tile_bbox_from_x_y(x, y)
        q = overpass_client._build_query(*coords)
        overpass_json = overpass_client.cache.get(f"{x}_{y}.json.gz", lambda: overpass_client._execute_query(q))
        json_data = overpass_client.overpass_to_soundscape_geojson(overpass_json)
        # with open("../reference/18747_25074.json") as f:
        #    json_data = json.load(f)

        assert len(json_data.keys()) == 2
        assert json_data["type"] == "FeatureCollection"
        assert len(json_data["features"]) > 0
        for feature in json_data["features"]:
            assert "feature_type" in feature
            assert "feature_value" in feature
            assert "geometry" in feature
            assert "osm_ids" in feature
            assert "properties" in feature
            assert "type" in feature

            assert "coordinates" in feature["geometry"]
            assert "type" in feature["geometry"]
