"""Acceptance checks (ACCEPTANCE.md / light-design "Why & what") against the generated `out/`.

Needs a prior live run:
  python3 -m generator --out out --extra-catalog old-version=fixtures/old-version.versions.toml
"""
import csv
import json
import os
import re
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
DATA = os.path.join(OUT, "data.json")
HTML = os.path.join(OUT, "dashboard.html")
RAW = os.path.join(OUT, "raw")
REFERENCE = os.path.join(ROOT, "reference", "direct-consumers.csv")
RUN_HINT = ("run `python3 -m generator --out out "
            "--extra-catalog old-version=fixtures/old-version.versions.toml` first")

CONSUMERS = ["oneapp-android", "navapp-automotive", "r2-navapp"]
DOCS_REPOS = ["mapdisplay-for-unity", "devportal-documentation"]
# Date-pinned baselines (2026-10-06): 2.4.5, 2.8.0-rc01 and the 12-behind fixture count below
# change with each go-sdk-android release; see ACCEPTANCE.md "Open decisions".
LATEST_STABLE, LATEST_RC = "2.4.5", "2.8.0-rc01"
DUO = "com.tomtom.sdk.maps:map-display-duo-internal"
KEY_RE = re.compile(r"key=[A-Za-z0-9_\-]{8,}")


class Generated(unittest.TestCase):
    _cache = None

    def setUp(self):
        if not os.path.exists(DATA) or not os.path.exists(HTML):
            self.fail(f"{DATA} or {HTML} missing: {RUN_HINT}")
        if Generated._cache is None:
            with open(DATA, encoding="utf-8") as fh:
                data_text = fh.read()
            with open(HTML, encoding="utf-8") as fh:
                html_text = fh.read()
            Generated._cache = (json.loads(data_text), data_text, html_text)
        self.data, self.data_text, self.html = Generated._cache

    def artifact(self, coordinate):
        found = [a for a in self.data["artifacts"] if a["coordinate"] == coordinate]
        self.assertEqual(len(found), 1, f"{coordinate} not listed exactly once in artifacts")
        return found[0]

    def section(self, title):
        """HTML of the <section> whose <h2> is `title`."""
        m = re.search(r"<section>\s*<h2>" + re.escape(title) + r"</h2>(.*?)</section>",
                      self.html, re.S)
        self.assertIsNotNone(m, f"no '{title}' section in dashboard.html")
        return m.group(1)


class AcceptanceTest(Generated):
    # M1 -----------------------------------------------------------------------------------
    def test_m1_direct_pairs_match_reference(self):
        with open(REFERENCE, newline="", encoding="utf-8") as fh:
            expected = {(r["repo"], r["artifact"]) for r in csv.DictReader(fh)}
        self.assertEqual(len(expected), 26)
        pairs = [(p["repo"], p["artifact"]) for p in self.data["direct_pairs"]]
        self.assertEqual(len(pairs), len(set(pairs)), "duplicate direct pairs")
        got = set(pairs)
        self.assertEqual(sorted(expected - got), [], "missing direct pairs")
        self.assertEqual(sorted(got - expected), [], "extra direct pairs")

    def test_m1_artifact_direct_consumers_match_reference(self):
        with open(REFERENCE, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        for coordinate in {r["artifact"] for r in rows}:
            want = sorted(r["repo"] for r in rows if r["artifact"] == coordinate)
            got = sorted(c["repo"] for c in self.artifact(coordinate)["consumers"]
                         if c["via"] is None)
            self.assertEqual(got, want, coordinate)

    # M2 -----------------------------------------------------------------------------------
    def test_m2_docs_repos_only_in_docs_references(self):
        self.assertEqual(sorted(self.data["docs_references"]), sorted(DOCS_REPOS))
        consumer_data = {k: v for k, v in self.data.items() if k != "docs_references"}
        blob = json.dumps(consumer_data)
        docs = self.section("Docs references")
        html_outside = self.html.replace(docs, "")
        for repo in DOCS_REPOS:
            self.assertNotIn(repo, blob, f"{repo} appears in consumer data")
            self.assertIn(repo, docs)
            self.assertNotIn(repo, html_outside, f"{repo} appears outside Docs references")

    # M3 -----------------------------------------------------------------------------------
    def test_m3_jpn_kor_styles_have_zero_direct_consumers(self):
        for artifact_id in ("map-display-premium-jpn-styles", "map-display-premium-kor-styles"):
            coordinate = f"com.tomtom.sdk.maps:{artifact_id}"
            a = self.artifact(coordinate)
            self.assertEqual([c for c in a["consumers"] if c["via"] is None], [])
            self.assertNotIn(coordinate, {p["artifact"] for p in self.data["direct_pairs"]})
            self.assertIn(coordinate, self.html)

    # M4 -----------------------------------------------------------------------------------
    def _assert_count_or_ahead(self, value, label):
        if isinstance(value, int):
            self.assertGreaterEqual(value, 0, f"negative releases-behind count for {label}")
        else:
            self.assertRegex(value, r"^ahead of ", f"bad releases-behind value for {label}")

    def test_m4_baselines(self):
        self.assertEqual(self.data["baselines"], {"stable": LATEST_STABLE, "rc": LATEST_RC})

    def test_m4_real_consumers_zero_behind_rc_and_ahead_of_stable(self):
        rows = {r["repo"]: r for r in self.data["consumer_versions"]}
        self.assertEqual(sorted(rows), sorted(CONSUMERS))
        for repo in CONSUMERS:
            self.assertEqual(rows[repo]["pinned"], LATEST_RC, repo)
            self.assertEqual(rows[repo]["behind_rc"], 0, repo)
            self.assertEqual(rows[repo]["behind_stable"], "ahead of stable", repo)

    def test_m4_old_version_fixture(self):
        [row] = [r for r in self.data["extra_consumers"] if r["name"] == "old-version"]
        self.assertEqual(row["pinned"], "2.6.0")
        self.assertEqual(row["behind_rc"], 12)  # date-pinned, see LATEST_STABLE above
        self.assertEqual(row["behind_stable"], "ahead of stable")

    def test_m4_no_negative_counts_and_html_shows_both_baselines(self):
        for row in self.data["consumer_versions"] + self.data["extra_consumers"]:
            label = row.get("repo") or row.get("name")
            self._assert_count_or_ahead(row["behind_stable"], label)
            self._assert_count_or_ahead(row["behind_rc"], label)
        versions = self.section("Consumer versions")
        self.assertIn(LATEST_STABLE, versions)
        self.assertIn(LATEST_RC, versions)
        for repo in CONSUMERS:
            self.assertRegex(versions, re.escape(repo) + r"</td><td>" + re.escape(LATEST_RC)
                             + r"</td><td>ahead of stable</td><td>0</td>")
        self.assertRegex(self.section("Extra catalogs"),
                         r"old-version</td><td>2\.6\.0</td><td>ahead of stable</td><td>12</td>")

    # M5 -----------------------------------------------------------------------------------
    def test_m5_outputs_contain_no_api_key(self):
        self.assertIsNone(KEY_RE.search(self.html), "API key in dashboard.html")
        self.assertIsNone(KEY_RE.search(self.data_text), "API key in data.json")

    # S1 -----------------------------------------------------------------------------------
    def test_s1_r2_navapp_transitive_via_duo_internal(self):
        for artifact_id in ("map-display-common", "map-display-standard", "map-display-premium"):
            coordinate = f"com.tomtom.sdk.maps:{artifact_id}"
            a = self.artifact(coordinate)
            self.assertIn({"repo": "r2-navapp", "via": DUO}, a["consumers"], coordinate)
            self.assertEqual(a["consumer_total"], len({c["repo"] for c in a["consumers"]}))
            self.assertIn({"repo": "r2-navapp", "artifact": coordinate, "via": DUO},
                          self.data["transitive_pairs"])
        self.assertIn("r2-navapp via <code>map-display-duo-internal</code>", self.html)

    def test_s1_transitive_never_duplicates_direct(self):
        direct = {(p["repo"], p["artifact"]) for p in self.data["direct_pairs"]}
        for p in self.data["transitive_pairs"]:
            self.assertNotIn((p["repo"], p["artifact"]), direct)
            self.assertIn((p["repo"], p["via"]), direct, "via must be a direct dependency")

    # S3 -----------------------------------------------------------------------------------
    def test_s3_unconsumed_artifacts_and_packages_listed(self):
        arts = self.data["artifacts"]
        zero = sorted(a["coordinate"] for a in arts if a["consumer_total"] == 0)
        self.assertEqual(sorted(self.data["unconsumed"]["artifacts"]), zero)
        for a in arts:
            if a["consumer_total"] == 0:
                self.assertEqual(a["consumers"], [], a["coordinate"])
        consumed_pkgs = {p for a in arts if a["consumer_total"] for p in a["packages"]}
        all_pkgs = {p for a in arts for p in a["packages"]}
        self.assertEqual(sorted(self.data["unconsumed"]["packages"]),
                         sorted(all_pkgs - consumed_pkgs))
        for jk in ("jpn", "kor"):
            self.assertIn(f"com.tomtom.sdk.maps:map-display-premium-{jk}-styles", zero)
        self.assertIn("com.tomtom.sdk.map.display.premium.jpn.styles",
                      self.data["unconsumed"]["packages"])
        section = self.section("No consumers")
        for item in zero + self.data["unconsumed"]["packages"]:
            self.assertIn(f"<code>{item}</code>", section)

    # S4 -----------------------------------------------------------------------------------
    def test_s4_internal_availability_column_and_total(self):
        raw_count, files = 0, 0
        for dirpath, _, names in os.walk(RAW):
            for name in names:
                if name != "state.csv":
                    continue
                files += 1
                with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
                    for line in fh:
                        parts = line.rstrip("\n").split(";")
                        if len(parts) >= 7 and parts[-3] == "INTERNAL_AVAILABILITY":
                            raw_count += 1
        self.assertGreater(files, 0, f"no state.csv files under {RAW}: {RUN_HINT}")
        self.assertGreater(raw_count, 0)
        model_total = sum(counts.get("INTERNAL_AVAILABILITY", 0)
                          for a in self.data["artifacts"] for counts in a["packages"].values())
        self.assertEqual(model_total, raw_count)
        self.assertEqual(self.data["state_totals"]["INTERNAL_AVAILABILITY"], raw_count)
        self.assertIn("<th>INTERNAL_AVAILABILITY</th>", self.html)
        totals = self.section("Stability totals")
        heads = re.findall(r"<th>([^<]*)</th>", totals)
        cells = re.findall(r'<td class="num">(\d+)</td>', totals)
        self.assertEqual(len(heads), len(cells))
        self.assertEqual(int(dict(zip(heads, cells))["INTERNAL_AVAILABILITY"]), raw_count)

    # S5 -----------------------------------------------------------------------------------
    def test_s5_consumed_visualization_modules_state_unknown(self):
        for artifact_id in ("navigation", "poi", "range"):
            coordinate = f"com.tomtom.sdk.maps.visualization:{artifact_id}"
            a = self.artifact(coordinate)
            self.assertEqual(a["stability"], "state unknown", coordinate)
            self.assertEqual(a["packages"], {}, coordinate)
            self.assertGreater(a["consumer_total"], 0, coordinate)
            row = re.search(r"<tr><td><code>" + re.escape(coordinate) + r"</code></td>.*?</tr>",
                            self.html)
            self.assertIsNotNone(row, coordinate)
            self.assertIn("state unknown", row.group(0))


class InjectedKeyTest(unittest.TestCase):
    """M5: a key injected into fetched inputs comes out obfuscated (offline, gh mocked)."""

    SECRET = "key=Zx9SECRETtoken_123"

    def fake_gh(self, args, **_):
        endpoint, s = args[2], self.SECRET
        if "/git/trees/" in endpoint:
            out = json.dumps({"truncated": False, "tree": [
                {"path": "maps/map-display-common/build.gradle.kts"},
                {"path": "maps/map-display-common/api/state.csv"}]})
        elif endpoint.endswith("/releases/latest"):
            out = "2.4.5\n"
        elif "/releases?" in endpoint:
            out = '{"tag_name":"2.4.5","draft":false}\n{"tag_name":"2.8.0-rc01","draft":false}\n'
        elif "contents/CODEOWNERS" in endpoint:
            # The last-match owner of map-display-common carries a key: it reaches the model.
            out = ("/maps/** @tomtom-internal/lp-mapvis-mapdisplaysdk-android\n"
                   f"/maps/map-display-common/ @tomtom-internal/team-{s}\n")
        elif endpoint.endswith("build.gradle.kts?ref=master"):
            out = ('val artifactId by extra("map-display-common")\n'
                   f'val groupId by extra("com.tomtom.sdk.maps")\n// https://x/?{s}\n')
        elif "api/state.csv" in endpoint:
            out = (f"c;d;com.tomtom.sdk.map.display.Url.load({s});fun;GA;true;\n"
                   "c;d;com.tomtom.sdk.map.display.X;class;INTERNAL_AVAILABILITY;true;\n")
        elif "versions.toml" in endpoint:
            out = (f'[versions]\ngosdk = "2.8.0-rc01"\n# {s}\n[libraries]\n'
                   'a = { module = "com.tomtom.sdk.maps:map-display-common", '
                   'version.ref = "gosdk" }\n')
        else:
            return subprocess.CompletedProcess(args, 1, stdout="", stderr="HTTP 404: Not Found")
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")

    def test_m5_injected_key_is_obfuscated(self):
        from generator import __main__ as cli
        from generator import github

        with tempfile.TemporaryDirectory() as tmp:
            extra = os.path.join(tmp, "extra.versions.toml")
            with open(extra, "w", encoding="utf-8") as fh:
                fh.write(f'[versions]\ngosdk = "2.6.0"  # {self.SECRET}\n[libraries]\n'
                         'a = { module = "com.tomtom.sdk.maps:map-display-common", '
                         'version.ref = "gosdk" }\n')
            out = os.path.join(tmp, "out")
            with mock.patch.object(github.subprocess, "run", side_effect=self.fake_gh):
                self.assertEqual(cli.main(["--out", out, "--extra-catalog", f"x={extra}"]), 0)
            texts = []
            for dirpath, _, names in os.walk(out):
                for name in names:
                    with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
                        texts.append((name, fh.read()))
        self.assertEqual(sorted(n for n, _ in texts), ["dashboard.html", "data.json", "state.csv"])
        for name, text in texts:
            self.assertIsNone(KEY_RE.search(text), f"API key in {name}")
        self.assertIn("key=***", dict(texts)["state.csv"])
        self.assertIn("team-key=***", dict(texts)["data.json"])
        self.assertIn("team-key=***", dict(texts)["dashboard.html"])

    def test_m5_output_stage_redacts_model(self):
        """A key that reaches the model unredacted is still obfuscated in both outputs."""
        from generator import __main__ as cli
        from generator import build

        model = {
            "baselines": {"stable": LATEST_STABLE, "rc": LATEST_RC},
            "artifacts": [{"coordinate": "com.tomtom.sdk.maps:x", "module": "maps/x",
                           "owner": f"team-{self.SECRET}", "stability": None,
                           "packages": {"com.tomtom.x": {"GA": 1}}, "consumers": [],
                           "consumer_total": 0}],
            "state_totals": {"GA": 1},
            "docs_references": [f"https://x/?{self.SECRET}"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out")
            with mock.patch.object(build, "collect", return_value=({}, {})), \
                    mock.patch.object(build, "assemble", return_value=model):
                self.assertEqual(cli.main(["--out", out]), 0)
            texts = {}
            for name in ("data.json", "dashboard.html"):
                with open(os.path.join(out, name), encoding="utf-8") as fh:
                    texts[name] = fh.read()
        for name, text in texts.items():
            self.assertNotIn("Zx9SECRETtoken_123", text, name)
            self.assertIsNone(KEY_RE.search(text), f"API key in {name}")
            self.assertIn("team-key=***", text, name)


if __name__ == "__main__":
    unittest.main()
