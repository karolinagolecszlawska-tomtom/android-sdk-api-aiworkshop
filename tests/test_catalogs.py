import pathlib
import unittest

from generator import catalogs

FIXTURE = pathlib.Path(__file__).resolve().parent.parent / "fixtures" / "old-version.versions.toml"

MIXED = """\
[versions]
gosdk = "2.8.0-rc01"
gosdkOld = "2.7.0-rc08"
kotlin = "2.0.0"

[libraries]
gosdk-maps = { module = "com.tomtom.sdk.maps:map-display-duo-internal", version.ref = "gosdk" }
mapDisplayDuo = { module = "com.tomtom.sdk.maps:map-display-duo-internal", version.ref = "gosdk" }
gosdk-routing={module="com.tomtom.sdk.maps.visualization:routing",version.ref="gosdkOld"}
gosdk-tilestore = { module = "com.tomtom.sdk.maps:map-tile-store", version = "2.8.0-rc01" }
safety = { module = "com.tomtom.sdk.safetylocations:safety-locations", version.ref = "gosdk" }
gosdkUtils = { module = "com.tomtom.automotive:gosdkUtils", version.ref = "gosdk" }
mapsLike = { module = "com.tomtom.sdk.mapsx:other", version.ref = "gosdk" }
kotlinStdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }
"""


class CatalogTest(unittest.TestCase):
    def test_fixture_resolves_gosdk_for_two_maps_libraries(self):
        libs = catalogs.parse_catalog(FIXTURE.read_text())
        self.assertEqual(libs, {
            "com.tomtom.sdk.maps:map-display-common": "2.6.0",
            "com.tomtom.sdk.maps:map-display-standard": "2.6.0",
        })
        self.assertEqual(catalogs.pinned_version(libs), "2.6.0")

    def test_non_maps_groups_dropped_and_aliases_deduped(self):
        libs = catalogs.parse_catalog(MIXED)
        self.assertEqual(sorted(libs), [
            "com.tomtom.sdk.maps.visualization:routing",
            "com.tomtom.sdk.maps:map-display-duo-internal",
            "com.tomtom.sdk.maps:map-tile-store",
        ])

    def test_no_space_inline_table_and_literal_version(self):
        libs = catalogs.parse_catalog(MIXED)
        self.assertEqual(libs["com.tomtom.sdk.maps.visualization:routing"], "2.7.0-rc08")
        self.assertEqual(libs["com.tomtom.sdk.maps:map-tile-store"], "2.8.0-rc01")

    def test_pinned_version_is_lowest_resolved(self):
        self.assertEqual(catalogs.pinned_version(catalogs.parse_catalog(MIXED)), "2.7.0-rc08")
        self.assertIsNone(catalogs.pinned_version({}))

    def test_consumer_catalog_files_are_fixed(self):
        self.assertEqual(catalogs.CONSUMER_CATALOGS, {
            "oneapp-android": "gradle/libs.versions.toml",
            "navapp-automotive": "gradle/gosdk-libs.versions.toml",
            "r2-navapp": "gradle/gosdk-libs.versions.toml",
        })


if __name__ == "__main__":
    unittest.main()
