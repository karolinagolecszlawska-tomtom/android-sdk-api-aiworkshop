import unittest

from generator import versions

# Release tags of go-sdk-android from 2.6.0 up to 2.8.0-rc01 (recon, 2026-10-06).
RECON_TAGS = [
    "2.4.5", "2.7.0-rc08", "2.8.0-rc01", "2.6.3", "2.5.7", "2.7.0-rc07", "2.6.2",
    "2.7.0-rc06", "2.6.1", "2.5.6", "2.6.0", "2.7.0-rc05", "2.7.0-rc04", "2.6.0-rc14",
    "2.7.0-rc03", "2.7.0-rc02", "2.7.0-rc01",
]


def rel(tag, draft=False):
    return {"tag_name": tag, "draft": draft}


class ReleaseTagsTest(unittest.TestCase):
    def test_drops_drafts_and_dev_tags(self):
        releases = [rel("2.9.0-dev034.g4d93d71c167d", draft=True), rel("2.8.0-rc01"),
                    rel("2.8.1", draft=True), rel("2.9.0-dev001"), rel("v2.3.0"), rel("2.4.5")]
        self.assertEqual(versions.release_tags(releases), ["2.4.5", "2.8.0-rc01"])

    def test_rc_sorts_before_stable_of_same_version(self):
        tags = versions.release_tags([rel("2.6.0"), rel("2.6.0-rc14"), rel("2.6.0-rc02"),
                                      rel("2.5.7"), rel("2.10.0-rc01")])
        self.assertEqual(tags, ["2.5.7", "2.6.0-rc02", "2.6.0-rc14", "2.6.0", "2.10.0-rc01"])

    def test_latest_rc_is_highest_semver_rc(self):
        tags = versions.release_tags([rel(t) for t in RECON_TAGS])
        self.assertEqual(versions.latest_rc(tags), "2.8.0-rc01")


class BehindTest(unittest.TestCase):
    def setUp(self):
        self.tags = versions.release_tags([rel(t) for t in RECON_TAGS])

    def test_old_version_fixture_is_12_behind_latest_rc(self):
        self.assertEqual(versions.behind("2.6.0", "2.8.0-rc01", self.tags, "RC"), 12)

    def test_pin_newer_than_stable_is_ahead(self):
        self.assertEqual(versions.behind("2.8.0-rc01", "2.4.5", self.tags, "stable"),
                         "ahead of stable")
        self.assertEqual(versions.behind("2.6.0", "2.4.5", self.tags, "stable"),
                         "ahead of stable")

    def test_pin_equal_to_baseline_is_zero(self):
        self.assertEqual(versions.behind("2.8.0-rc01", "2.8.0-rc01", self.tags, "RC"), 0)

    def test_older_pin_counts_tags_up_to_baseline(self):
        self.assertEqual(versions.behind("2.7.0-rc06", "2.7.0-rc08", self.tags, "RC"), 2)


if __name__ == "__main__":
    unittest.main()
