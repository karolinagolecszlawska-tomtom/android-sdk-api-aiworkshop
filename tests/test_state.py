import unittest

from generator import state

# Rows in the shape of go-sdk-android maps/map-display-standard/api/state.csv.
STATE_CSV = """\
module_name;domain;name;type;state;hasDoc;flavor
maps:map-display-standard;Map Vis;com.tomtom.sdk.map.display.StandardMapRendererCompat.kt.StandardMapRendererCompat(Context,MapTileInfrastructure,Int,InitialCameraOptions,StandardMapRendererCompatConfiguration.()->Unit=):MapRendererCompat;FUNCTION;BETA;YES;EXTENDED
maps:map-display-standard;Map Vis;com.tomtom.sdk.map.display.StandardMapRendererCompatConfiguration;CLASS;BETA;YES;EXTENDED
maps:map-display-standard;Map Vis;com.tomtom.sdk.map.display.StandardMapRendererCompatConfiguration.mapStyle:StyleDescriptor?;PROPERTY;GA;YES;EXTENDED
maps:map-display-standard;Map Vis;com.tomtom.sdk.map.display.style.StyleMode;CLASS;INTERNAL_AVAILABILITY;YES;EXTENDED
maps:map-display-standard;Map Vis;com.tomtom.sdk.map.display.style.StyleMode.DARK;ENUM_ENTRY;INTERNAL_AVAILABILITY;YES;EXTENDED
maps:map-display-standard;Map Vis;com.tomtom.sdk.map.display.style.StyleMode.LIGHT;ENUM_ENTRY;INTERNAL;NO;EXTENDED

"""


class ParseRowsTest(unittest.TestCase):
    def test_semicolon_split_keeps_commas_in_names(self):
        rows = state.parse_rows(STATE_CSV)
        self.assertEqual(len(rows), 6)
        first = rows[0]
        self.assertEqual(first["module_name"], "maps:map-display-standard")
        self.assertTrue(first["name"].startswith(
            "com.tomtom.sdk.map.display.StandardMapRendererCompat.kt.StandardMapRendererCompat(Context,"))
        self.assertTrue(first["name"].endswith("):MapRendererCompat"))
        self.assertEqual(first["type"], "FUNCTION")
        self.assertEqual(first["state"], "BETA")
        self.assertEqual(first["flavor"], "EXTENDED")


class PackageOfTest(unittest.TestCase):
    def test_file_facade_row(self):
        self.assertEqual(state.package_of(
            "com.tomtom.sdk.map.display.StandardMapRendererCompat.kt.StandardMapRendererCompat"
            "(Context,SdkContext,Int):MapRendererCompat"), "com.tomtom.sdk.map.display")

    def test_class_and_member_rows(self):
        self.assertEqual(state.package_of("com.tomtom.sdk.map.display.style.StyleMode.DARK"),
                         "com.tomtom.sdk.map.display.style")
        self.assertEqual(state.package_of(
            "com.tomtom.sdk.map.display.StandardMapRendererCompatConfiguration.mapStyle:StyleDescriptor?"),
            "com.tomtom.sdk.map.display")

    def test_lowercase_inside_parentheses_ignored(self):
        self.assertEqual(state.package_of("com.tomtom.sdk.maps.Foo.bar(com.tomtom.x.y):Unit"),
                         "com.tomtom.sdk.maps")


class TallyTest(unittest.TestCase):
    def test_tally_per_package_and_state_with_internal_availability_separate(self):
        self.assertEqual(state.tally(STATE_CSV), {
            "com.tomtom.sdk.map.display": {"BETA": 2, "GA": 1},
            "com.tomtom.sdk.map.display.style": {"INTERNAL_AVAILABILITY": 2, "INTERNAL": 1},
        })

    def test_module_with_state_csv(self):
        result = state.module_stability(STATE_CSV)
        self.assertIsNone(result["stability"])
        self.assertEqual(result["packages"], state.tally(STATE_CSV))

    def test_missing_state_csv_is_state_unknown(self):
        self.assertEqual(state.module_stability(None),
                         {"stability": "state unknown", "packages": {}})
        self.assertEqual(state.STATE_UNKNOWN, "state unknown")


if __name__ == "__main__":
    unittest.main()
