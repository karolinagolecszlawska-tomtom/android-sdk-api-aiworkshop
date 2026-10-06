import re
import unittest

from generator import html as dashboard_html

DUO = "com.tomtom.sdk.maps:map-display-duo-internal"

MODEL = {
    "baselines": {"stable": "2.4.5", "rc": "2.8.0-rc01"},
    "artifacts": [
        {
            "coordinate": DUO,
            "module": "maps/map-display-duo-internal",
            "owner": "lp-mapvis-mapdisplaysdk-android",
            "stability": None,
            "packages": {"com.tomtom.sdk.map.display.duo": {"GA": 4}},
            "consumers": [{"repo": "r2-navapp", "via": None}],
            "consumer_total": 1,
        },
        {
            "coordinate": "com.tomtom.sdk.maps:map-display-common",
            "module": "maps/map-display-common",
            "owner": "lp-mapvis-mapdisplaysdk-android",
            "stability": None,
            "packages": {"com.tomtom.sdk.map.display": {"GA": 10, "BETA": 2,
                                                        "INTERNAL_AVAILABILITY": 3}},
            "consumers": [{"repo": "oneapp-android", "via": None},
                          {"repo": "r2-navapp", "via": DUO}],
            "consumer_total": 2,
        },
        {
            "coordinate": "com.tomtom.sdk.maps.visualization:navigation",
            "module": "maps/visualization/navigation",
            "owner": "go-sdk-android-maps-vismods",
            "stability": "state unknown",
            "packages": {},
            "consumers": [{"repo": "navapp-automotive", "via": None}],
            "consumer_total": 1,
        },
        {
            "coordinate": "com.tomtom.sdk.maps:map-display-premium-jpn-styles",
            "module": "maps/map-display-premium-jpn-styles",
            "owner": "lp-mapvis-mapdisplaysdk-android",
            "stability": None,
            "packages": {"com.tomtom.sdk.map.display.style.jpn": {"GA": 1}},
            "consumers": [],
            "consumer_total": 0,
        },
    ],
    "consumer_versions": [
        {"repo": "r2-navapp", "pinned": "2.8.0-rc01", "behind_stable": "ahead of stable",
         "behind_rc": 0},
    ],
    "unconsumed": {
        "artifacts": ["com.tomtom.sdk.maps:map-display-premium-jpn-styles"],
        "packages": ["com.tomtom.sdk.map.display.style.jpn"],
    },
    "docs_references": ["mapdisplay-for-unity", "devportal-documentation"],
    "extra_consumers": [
        {"name": "old-version", "pinned": "2.6.0", "behind_stable": "ahead of stable",
         "behind_rc": 12, "artifacts": ["com.tomtom.sdk.maps:map-display-common"]},
    ],
}


def section(page, title):
    """Text of the <section> whose heading is `title`."""
    m = re.search(r"<section[^>]*>\s*<h2>" + re.escape(title) + r"</h2>(.*?)</section>",
                  page, re.S)
    return m.group(1) if m else ""


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.page = dashboard_html.render(MODEL)

    def test_self_contained_document(self):
        self.assertTrue(self.page.lstrip().lower().startswith("<!doctype html>"))
        self.assertIn("<style>", self.page)
        self.assertNotIn("<script", self.page)

    def test_grouped_by_package(self):
        self.assertIn("<h3>com.tomtom.sdk.map.display</h3>", self.page)
        self.assertIn("<h3>com.tomtom.sdk.map.display.duo</h3>", self.page)

    def test_state_columns_include_internal_availability(self):
        self.assertIn("<th>INTERNAL_AVAILABILITY</th>", self.page)

    def test_transitive_consumer_shown_via_artifact(self):
        self.assertIn("r2-navapp via <code>map-display-duo-internal</code>", self.page)

    def test_state_unknown_shown(self):
        self.assertIn("state unknown", self.page)
        self.assertIn("com.tomtom.sdk.maps.visualization:navigation", self.page)

    def test_consumer_versions_section(self):
        versions = section(self.page, "Consumer versions")
        self.assertIn("r2-navapp", versions)
        self.assertIn("ahead of stable", versions)
        self.assertIn("2.4.5", versions)
        self.assertIn("2.8.0-rc01", versions)

    def test_no_consumers_section(self):
        unconsumed = section(self.page, "No consumers")
        self.assertIn("com.tomtom.sdk.maps:map-display-premium-jpn-styles", unconsumed)
        self.assertIn("com.tomtom.sdk.map.display.style.jpn", unconsumed)

    def test_docs_references_section_lists_both_repos(self):
        docs = section(self.page, "Docs references")
        self.assertIn("mapdisplay-for-unity", docs)
        self.assertIn("devportal-documentation", docs)

    def test_extra_catalogs_section_when_present(self):
        extra = section(self.page, "Extra catalogs")
        self.assertIn("old-version", extra)
        self.assertIn("12", extra)
        no_extra = dashboard_html.render(dict(MODEL, extra_consumers=[]))
        self.assertNotIn("<h2>Extra catalogs</h2>", no_extra)

    def test_text_is_escaped(self):
        page = dashboard_html.render(dict(MODEL, docs_references=["<b>x</b>"]))
        self.assertIn("&lt;b&gt;x&lt;/b&gt;", page)

    def test_no_key_in_output(self):
        model = dict(MODEL, docs_references=MODEL["docs_references"]
                     + ["https://example.com/?key=abcdef123456"])
        page = dashboard_html.render(model)
        self.assertNotRegex(page, r"key=[A-Za-z0-9_\-]{8,}")
        self.assertIn("key=***", page)


if __name__ == "__main__":
    unittest.main()
