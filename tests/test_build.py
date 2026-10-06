import json
import subprocess
import unittest
from unittest import mock

from generator import build, github
from generator.codeowners import Codeowners

TEAM = "@tomtom-internal/lp-mapvis-mapdisplaysdk-android"
CODEOWNERS = f"""
/maps/** {TEAM}
/maps/visualization/ @tomtom-internal/go-sdk-android-maps-vismods
"""


def gradle(group, artifact, *api):
    deps = "\n".join(f"    api(projects.{a})" for a in api)
    return (f'val artifactId by extra("{artifact}")\nval groupId by extra("{group}")\n'
            f"dependencies {{\n{deps}\n    implementation(projects.maps.mapDisplayLeaf)\n}}\n")


G = "com.tomtom.sdk.maps"
DUO, COMMON, STANDARD, LEAF, JPN = (f"{G}:map-display-duo-internal", f"{G}:map-display-common",
                                    f"{G}:map-display-standard", f"{G}:map-display-leaf",
                                    f"{G}:map-display-premium-jpn-styles")
NAV = "com.tomtom.sdk.maps.visualization:navigation"

GRADLE = {
    "maps/map-display-duo-internal": gradle(G, "map-display-duo-internal",
                                            "maps.mapDisplayCommon", "maps.mapDisplayStandard",
                                            "core.notMaps"),
    "maps/map-display-common": gradle(G, "map-display-common"),
    # standard -> leaf is a second level from duo: must not be followed.
    "maps/map-display-standard": gradle(G, "map-display-standard", "maps.mapDisplayLeaf"),
    "maps/map-display-leaf": gradle(G, "map-display-leaf"),
    "maps/map-display-premium-jpn-styles": gradle(G, "map-display-premium-jpn-styles"),
    "maps/visualization/navigation": gradle("com.tomtom.sdk.maps.visualization", "navigation"),
    "maps/docs": "plugins { }\n",  # unpublished
}
TREE = [f"{m}/build.gradle.kts" for m in GRADLE] + ["core/x/build.gradle.kts"]

STATE_HDR = "module_name;domain;name;type;state;hasDoc;flavor\n"
STATE = {
    "maps/map-display-duo-internal": STATE_HDR + "duo;d;com.tomtom.sdk.map.display.duo.Duo;class;GA;true;\n",
    "maps/map-display-common": STATE_HDR
    + "c;d;com.tomtom.sdk.map.display.MapView;class;GA;true;\n"
    + "c;d;com.tomtom.sdk.map.display.MapView.foo(a, b);fun;INTERNAL_AVAILABILITY;true;\n",
    "maps/map-display-standard": STATE_HDR + "s;d;com.tomtom.sdk.map.display.std.S;class;BETA;true;\n",
    "maps/map-display-leaf": STATE_HDR + "l;d;com.tomtom.sdk.map.display.leaf.L;class;GA;true;\n",
    "maps/map-display-premium-jpn-styles": STATE_HDR
    + "j;d;com.tomtom.sdk.map.display.style.jpn.J;class;GA;true;\n",
    "maps/visualization/navigation": None,
}


def catalog(version, *coords):
    libs = "\n".join(f'l{i} = {{ module = "{c}", version.ref = "gosdk" }}'
                     for i, c in enumerate(coords))
    return f'[versions]\ngosdk = "{version}"\n[libraries]\n{libs}\n'


CATALOGS = {
    "oneapp-android": catalog("2.8.0-rc01", COMMON, f"{G}:map-display-common"),
    "navapp-automotive": catalog("2.8.0-rc01", NAV, COMMON),
    "r2-navapp": catalog("2.8.0-rc01", DUO),
}
TAGS = ["2.4.5", "2.6.0", "2.6.1", "2.7.0-rc01", "2.8.0-rc01"]
RELEASES = [{"tag_name": t, "draft": False} for t in TAGS] + [
    {"tag_name": "2.9.0-dev1", "draft": True}]


def model(**overrides):
    kwargs = dict(codeowners_text=CODEOWNERS, published=build.published_modules(GRADLE),
                  gradle_texts=GRADLE, state_texts=STATE, catalogs=CATALOGS, releases=RELEASES, latest_tag="2.4.5",
                  extra_catalogs={"old-version": catalog("2.6.0", COMMON, STANDARD)})
    kwargs.update(overrides)
    return build.assemble(**kwargs)


def art(m, coordinate):
    return next(a for a in m["artifacts"] if a["coordinate"] == coordinate)


class AssembleTest(unittest.TestCase):
    def setUp(self):
        self.m = model()

    def test_artifacts_are_published_in_scope_modules(self):
        self.assertEqual({a["coordinate"] for a in self.m["artifacts"]},
                         {DUO, COMMON, STANDARD, LEAF, JPN, NAV})
        self.assertEqual(art(self.m, NAV)["owner"], "go-sdk-android-maps-vismods")
        self.assertEqual(art(self.m, DUO)["owner"], "lp-mapvis-mapdisplaysdk-android")

    def test_in_scope_modules_from_codeowners_and_tree(self):
        self.assertEqual(build.in_scope_modules(Codeowners(CODEOWNERS), TREE), sorted(GRADLE))

    def test_published_modules_skip_unpublished(self):
        published = build.published_modules(GRADLE)
        self.assertNotIn("maps/docs", published)
        self.assertEqual(published["maps/visualization/navigation"], NAV)

    def test_catalog_without_mapvis_libraries_fails_loudly(self):
        with self.assertRaises(ValueError):
            model(extra_catalogs={"empty": '[versions]\ngosdk = "2.6.0"\n'})

    def test_direct_pairs_from_catalogs_deduped(self):
        self.assertEqual(
            sorted((p["repo"], p["artifact"]) for p in self.m["direct_pairs"]),
            sorted([("oneapp-android", COMMON), ("navapp-automotive", NAV),
                    ("navapp-automotive", COMMON), ("r2-navapp", DUO)]))

    def test_transitive_one_level_via_artifact(self):
        pairs = {(p["repo"], p["artifact"]): p["via"] for p in self.m["transitive_pairs"]}
        self.assertEqual(pairs, {("r2-navapp", COMMON): DUO, ("r2-navapp", STANDARD): DUO})
        # standard is consumed only transitively, so standard -> leaf (two levels) is not followed.
        self.assertEqual(art(self.m, LEAF)["consumers"], [])

    def test_transitive_does_not_duplicate_direct(self):
        cats = dict(CATALOGS, **{"r2-navapp": catalog("2.8.0-rc01", DUO, COMMON)})
        m = model(catalogs=cats)
        self.assertNotIn(("r2-navapp", COMMON),
                         {(p["repo"], p["artifact"]) for p in m["transitive_pairs"]})
        self.assertEqual([c for c in art(m, COMMON)["consumers"] if c["repo"] == "r2-navapp"],
                         [{"repo": "r2-navapp", "via": None}])

    def test_totals_count_direct_and_transitive(self):
        self.assertEqual(art(self.m, COMMON)["consumer_total"], 3)  # oneapp, navapp + r2 via duo
        self.assertIn({"repo": "r2-navapp", "via": DUO}, art(self.m, COMMON)["consumers"])
        self.assertEqual(art(self.m, STANDARD)["consumer_total"], 1)  # r2 via duo
        self.assertEqual(art(self.m, DUO)["consumer_total"], 1)
        self.assertEqual(art(self.m, JPN)["consumer_total"], 0)

    def test_unconsumed_artifacts_and_packages(self):
        self.assertEqual(sorted(self.m["unconsumed"]["artifacts"]), sorted([JPN, LEAF]))
        self.assertEqual(sorted(self.m["unconsumed"]["packages"]),
                         ["com.tomtom.sdk.map.display.leaf", "com.tomtom.sdk.map.display.style.jpn"])

    def test_extra_catalogs_kept_out_of_direct_pairs(self):
        repos = {p["repo"] for p in self.m["direct_pairs"] + self.m["transitive_pairs"]}
        self.assertNotIn("old-version", repos)
        self.assertNotIn("old-version", {r["repo"] for r in self.m["consumer_versions"]})
        for a in self.m["artifacts"]:
            self.assertNotIn("old-version", {c["repo"] for c in a["consumers"]})
        [extra] = self.m["extra_consumers"]
        self.assertEqual(extra["name"], "old-version")
        self.assertEqual(extra["pinned"], "2.6.0")
        self.assertEqual(extra["behind_rc"], 3)  # 2.6.1, 2.7.0-rc01, 2.8.0-rc01
        self.assertEqual(extra["behind_stable"], "ahead of stable")
        self.assertEqual(sorted(extra["artifacts"]), sorted([COMMON, STANDARD]))

    def test_baselines_and_consumer_versions(self):
        self.assertEqual(self.m["baselines"], {"stable": "2.4.5", "rc": "2.8.0-rc01"})
        for row in self.m["consumer_versions"]:
            self.assertEqual(row["pinned"], "2.8.0-rc01")
            self.assertEqual(row["behind_rc"], 0)
            self.assertEqual(row["behind_stable"], "ahead of stable")
        self.assertEqual(sorted(r["repo"] for r in self.m["consumer_versions"]),
                         sorted(CATALOGS))

    def test_stability_and_state_totals(self):
        self.assertEqual(art(self.m, NAV)["stability"], "state unknown")
        self.assertEqual(art(self.m, COMMON)["packages"],
                         {"com.tomtom.sdk.map.display": {"GA": 1, "INTERNAL_AVAILABILITY": 1}})
        self.assertEqual(self.m["state_totals"]["INTERNAL_AVAILABILITY"], 1)
        self.assertEqual(self.m["state_totals"]["GA"], 4)

    def test_docs_references_fixed_and_never_consumers(self):
        self.assertEqual(self.m["docs_references"],
                         ["mapdisplay-for-unity", "devportal-documentation"])

    def test_model_is_json_serialisable(self):
        json.dumps(self.m)


class CollectTest(unittest.TestCase):
    """collect() fetches state.csv only for published modules (D-12)."""

    def test_unpublished_module_state_csv_not_fetched_nor_counted(self):
        docs_state = STATE_HDR + "x;d;com.tomtom.docs.D;class;INTERNAL_AVAILABILITY;true;\n"
        files = {"CODEOWNERS": CODEOWNERS, "maps/docs/api/state.csv": docs_state}
        files.update({f"{m}/build.gradle.kts": t for m, t in GRADLE.items()})
        files.update({f"{m}/api/state.csv": t for m, t in STATE.items() if t is not None})
        tree = TREE + [p for p in files if p.endswith("/api/state.csv")]
        fetched = []

        def raw(repo, path, ref=None):
            fetched.append(path)
            if repo != github.SDK_REPO:
                return CATALOGS[repo]
            return files.get(path)

        with mock.patch.object(github, "tree", return_value=tree), \
                mock.patch.object(github, "raw", side_effect=raw), \
                mock.patch.object(github, "releases", return_value=RELEASES), \
                mock.patch.object(github, "latest_release", return_value="2.4.5"):
            kwargs, raw_states = build.collect()
        self.assertNotIn("maps/docs/api/state.csv", fetched)
        self.assertIn("maps/map-display-common/api/state.csv", fetched)
        self.assertNotIn("maps/docs", raw_states)
        self.assertNotIn("maps/docs", kwargs["state_texts"])
        self.assertEqual(set(raw_states), {m for m, t in STATE.items() if t is not None})
        m = build.assemble(**kwargs)
        self.assertEqual(m["state_totals"]["INTERNAL_AVAILABILITY"], 1)


class GithubTest(unittest.TestCase):
    def _run(self, stdout):
        return mock.patch.object(github.subprocess, "run", return_value=subprocess.CompletedProcess(
            [], 0, stdout=stdout, stderr=""))

    def test_raw_is_redacted(self):
        with self._run("url = https://x/?key=abcdef123456XYZ\n"):
            text = github.raw("r2-navapp", "gradle/x.toml")
        self.assertEqual(text, "url = https://x/?key=***\n")

    def test_every_call_is_get_only(self):
        calls = {
            "raw": (lambda: github.raw("r2-navapp", "gradle/x.toml"), "x\n"),
            "tree": (lambda: github.tree("go-sdk-android", "master"),
                     json.dumps({"truncated": False, "tree": [{"path": "a"}]})),
            "releases": (github.releases, '{"tag_name": "2.4.5", "draft": false}\n'),
            "latest_release": (github.latest_release, "2.4.5\n"),
        }
        for name, (call, stdout) in calls.items():
            with self.subTest(name), self._run(stdout) as run:
                call()
                args = run.call_args.args[0]
                self.assertEqual(args[:2], ["gh", "api"])
                for flag in ("--method", "-X", "-f", "-F", "--field", "--raw-field", "--input"):
                    self.assertNotIn(flag, args)

    def test_raw_missing_file_returns_none(self):
        err = subprocess.CompletedProcess([], 1, stdout="", stderr="HTTP 404: Not Found")
        with mock.patch.object(github.subprocess, "run", return_value=err):
            self.assertIsNone(github.raw("go-sdk-android", "maps/x/api/state.csv", ref="master"))

    def test_raw_error_merely_containing_404_raises(self):
        err = subprocess.CompletedProcess([], 1, stdout="",
                                          stderr="HTTP 502: Bad Gateway (request 40412)")
        with mock.patch.object(github.subprocess, "run", return_value=err):
            with self.assertRaises(RuntimeError):
                github.raw("go-sdk-android", "CODEOWNERS", ref="master")

    def test_raw_other_error_raises(self):
        err = subprocess.CompletedProcess([], 1, stdout="", stderr="HTTP 401: Bad credentials")
        with mock.patch.object(github.subprocess, "run", return_value=err):
            with self.assertRaises(RuntimeError):
                github.raw("go-sdk-android", "CODEOWNERS", ref="master")


if __name__ == "__main__":
    unittest.main()
