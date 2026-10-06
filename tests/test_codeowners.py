import unittest

from generator.codeowners import TEAM, Codeowners

# Excerpt of go-sdk-android CODEOWNERS (master, 2026-10-06), alignment shortened.
CODEOWNERS = """\
# Please see docs for more information.
CODEOWNERS   @tomtom-internal/nav-sdk-tech-lt
/apps/maps-demo-app/   @tomtom-internal/lp-mapvis-mapdisplaysdk-android
/geojson/   @tomtom-internal/go-sdk-android-core-search   # Concrete team: Search
/maps/   @tomtom-internal/lp-mapvis-mapdisplaysdk-android
/maps/docs/   @tomtom-internal/lp-mapvis-mapdisplaysdk-android
/maps/map-display-common/**/GeoJson*   @tomtom-internal/go-sdk-android-maps-vismods
/maps/map-display-standard-binding-internal/   @tomtom-internal/t4g_mapvis-renderingengine
# /maps/**/module.md   @tomtom-internal/lp-mapvis-mapdisplaysdk-android
/maps/maps-visualization-integration-tests   @tomtom-internal/go-sdk-android-maps-vismods @tomtom-internal/lp-mapvis-mapdisplaysdk-android
/maps/visualization/   @tomtom-internal/go-sdk-android-maps-vismods   # Concrete team: MapVis: GO MapVis team
/maps/visualization/**/*Alternative*   @tomtom-internal/go-sdk-android-maps-vismods
/maps/visualization/poi/   @tomtom-internal/lp-mapvis-mapdisplaysdk-android
/maps/visualization/visualization/**/poi/   @tomtom-internal/lp-mapvis-mapdisplaysdk-android
*.md   @tomtom-internal/docs-team
"""


class CodeownersTest(unittest.TestCase):
    def setUp(self):
        self.co = Codeowners(CODEOWNERS)

    def test_team_paths_lists_patterns_naming_the_team(self):
        self.assertEqual(self.co.team_paths(TEAM), [
            "/apps/maps-demo-app/",
            "/maps/",
            "/maps/docs/",
            "/maps/maps-visualization-integration-tests",
            "/maps/visualization/poi/",
            "/maps/visualization/visualization/**/poi/",
        ])

    def test_commented_lines_and_trailing_comments_ignored(self):
        self.assertNotIn("/maps/**/module.md", self.co.team_paths(TEAM))
        self.assertEqual(self.co.owner_of("geojson/"), "go-sdk-android-core-search")

    def test_last_match_wins_for_visualization_routing(self):
        self.assertEqual(self.co.owner_of("/maps/visualization/routing/"),
                         "go-sdk-android-maps-vismods")
        self.assertEqual(self.co.owner_of("maps/visualization/routing"),
                         "go-sdk-android-maps-vismods")

    def test_more_specific_later_rule_overrides(self):
        self.assertEqual(self.co.owner_of("maps/visualization/poi"),
                         "lp-mapvis-mapdisplaysdk-android")
        self.assertEqual(self.co.owner_of("maps/map-display-standard-binding-internal"),
                         "t4g_mapvis-renderingengine")
        self.assertEqual(self.co.owner_of("maps/map-display-common"),
                         "lp-mapvis-mapdisplaysdk-android")

    def test_double_star_globs_do_not_match_the_module_directory_itself(self):
        # /maps/visualization/visualization/**/poi/ only matches deeper poi dirs.
        self.assertEqual(self.co.owner_of("maps/visualization/visualization"),
                         "go-sdk-android-maps-vismods")
        self.assertEqual(self.co.owner_of("maps/visualization/visualization/src/main/poi"),
                         "lp-mapvis-mapdisplaysdk-android")

    def test_unanchored_glob_matches_anywhere(self):
        self.assertEqual(self.co.owner_of("maps/docs/README.md"), "docs-team")

    def test_multiple_owners_are_all_reported(self):
        self.assertEqual(self.co.owner_of("maps/maps-visualization-integration-tests/app"),
                         "go-sdk-android-maps-vismods, lp-mapvis-mapdisplaysdk-android")

    def test_unowned_path(self):
        self.assertIsNone(self.co.owner_of("navigation/core"))

    def test_in_scope_when_any_team_pattern_matches(self):
        self.assertTrue(self.co.in_scope("maps/visualization/routing", TEAM))
        self.assertTrue(self.co.in_scope("maps/map-display-standard-binding-internal", TEAM))
        self.assertFalse(self.co.in_scope("geojson", TEAM))
        self.assertFalse(self.co.in_scope("apps/adas-demo-app", TEAM))


if __name__ == "__main__":
    unittest.main()
