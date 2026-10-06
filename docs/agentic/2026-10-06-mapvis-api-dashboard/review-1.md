# Review: 2026-10-06-mapvis-api-dashboard — run 1

**Date:** 2026-10-06
**Artifact:** review
**Verdict:** APPROVED — no blocking findings
**Rounds:** 2
**Feature artifacts:** light-design.md
**Default branch:** origin/main
**Base SHA:** ee1aef5dc3d87c3ea070d1c4f26aeb9390803ddb
**Head SHA:** cce91d53ae32e549c3ff8740836fb83c7f3de0ae
**Reviewer model:** sonnet
**Challenger model:** opus
**Brief-writer model:** opus
**Template version:** default/0.1.0

**Plugin version:** 0.5.2
**Agent Sessions:** claude-code: 0a4822dc-4eb8-4322-b7d6-49681b35bdd2

---

## What changed

<!-- brief:what-changed -->
The MapVis team cannot see which Android apps consume each `go-sdk-android` artifact, how stable the consumed packages are, or how far each app lags behind SDK releases (`light-design.md:12`). This change adds a Python standard-library generator that reads `go-sdk-android` and three consumer repos through `gh api` GET calls and writes `out/dashboard.html` and `out/data.json`, grouped by package (`light-design.md:28-39`). It covers rules M1-M5, S1, S3, S4, S5, N1 and N2; S2 and the weekly refresh are deferred (`light-design.md:58`).
<!-- /brief:what-changed -->

## Where human judgement is needed

<!-- brief:human-judgement -->
`tests/test_acceptance.py:39` skips every rule check when `out/data.json` is missing, while `light-design.md:40` says the test fails; you decide which behaviour the verify commands should have (F-16, F-22 in `round-2.json`).
`tests/test_acceptance.py:29` hardcodes `2.4.5`, `2.8.0-rc01` and 12-behind against live data, so the next SDK release makes it fail; you decide whether that is the intended snapshot (F-21, `round-2.json`).
`generator/build.py:242` and `generator/versions.py:37` abort the whole run on one unusable pin or no RC tag; deviation 1 (`light-design.md:77`) chose to fail loudly, and you decide whether that holds per consumer (F-5, F-7, `round-2.json`).
`generator/redact.py:4` masks only `key=` plus 8 or more word characters, the shape M5 names; you decide whether other key shapes matter here (F-14, `round-2.json`).
`generator/catalogs.py:30` keeps only `module=` tables, matching the fixed catalogs of D-9 (`light-design.md:66`); you decide whether other notations must be reported (F-1, `round-2.json`).
<!-- /brief:human-judgement -->

## What was not verified

<!-- brief:not-verified -->
All 24 findings in `round-2.json` reached you with verdict "not challenged" and none was tool-proved. Reviewers did not see `light-design.md` (`scope.json` "withheld"), except docs-coherence, which read only that file. `.gitignore` matched no path pattern (`scope.json` "unmatched_paths"). Correctness checked only the first half of `tests/test_build.py` (`round-2.json` coverage).
<!-- /brief:not-verified -->

---

## Rounds

| Round | Critical | Major | Minor | Action | Fix commits |
|-------|----------|-------|-------|--------|-------------|
| 1 | 0 | 1 | 18 | fix | 1 |
| 2 | 0 | 0 | 24 | stop | 0 |

## Findings

Round 2.

| ID | Severity | Verdict | Dimension | Also flagged by | Site | Summary | Effect | Evidence |
|----|----------|---------|-----------|-----------------|------|---------|--------|----------|
| F-3 | minor | not challenged | correctness | testability | `generator/state.py:14` | parse_rows silently drops any line with fewer than 7 `;` fields instead of failing or counting it, so malformed rows are omitted from the stability tallies | Stability counts (including INTERNAL_AVAILABILITY totals) can be understated with no indication on the dashboard. |  |
| F-1 | minor | not challenged | correctness |  | `generator/catalogs.py:30` | parse_catalog silently skips libraries not written as a table with `module=` (string form "group:name:version" or `group=`/`name=` tables), so those consumers vanish from direct_pairs with no error | A consumer using another catalog notation would be missing from the dashboard and its artifacts shown as unconsumed, with no warning. |  |
| F-2 | minor | not challenged | correctness |  | `generator/modules.py:27` | accessor_to_path inserts a hyphen before every capital, so Gradle accessors with acronyms or digits (e.g. mapDisplayUI) map to a nonexistent path and api_deps drops the dependency via the `path in in_scope` filter without any error | A transitive consumer relationship (via) could be silently missing, understating an artifact's consumer total. |  |
| F-4 | minor | not challenged | correctness |  | `generator/__main__.py:34` | out/raw is never cleared before writing, so state.csv files from modules that no longer have one (or were removed) remain from earlier runs; the S4 acceptance test walks out/raw and tallies them | A stale out/ directory can make the S4 check compare the model against leftover files and fail or pass wrongly. |  |
| F-5 | minor | not challenged | correctness |  | `generator/versions.py:37` | behind() calls tag_key(baseline) unguarded; latest_rc returns None when no -rc tag exists, so the whole run crashes with 'not a release tag: None' instead of reporting no RC baseline | Generation aborts without producing a dashboard if the SDK has no RC release published. |  |
| F-6 | minor | not challenged | contracts |  | `generator/build.py:319` | gradle_texts values come straight from github.raw, which returns None on a 404 (github.py:496-500), but published_modules (parse_module regex .search) and assemble line 229 (api_deps findall via .get(m, "") returns None for a present key) assume str, so a build file that 404s despite being in the tree raises TypeError. | A transient or racing 404 on one module's build file aborts the whole generator run with a traceback instead of skipping that module or naming it. |  |
| F-7 | minor | not challenged | contracts |  | `generator/build.py:242` | pinned_version returns None for a catalog with no kept MapVis libraries (catalogs.py:387), and _version_row passes it to behind -> tag_key, which raises ValueError (versions.py:821); a non-release pin such as a SNAPSHOT or a version given as a table also hits this, for real consumers and for --extra-catalog at line 278. | One consumer catalog that drops all maps libraries or pins a non-release version stops the whole dashboard from being generated, with a bare ValueError that does not say which repo. |  |
| F-8 | minor | not challenged | contracts |  | `generator/state.py:796` | package_of returns an empty string when the name has no leading lowercase segment, and tally uses it as a package key; html._packages (html.py:605) and build's unconsumed package set (build.py:266-267) assume non-empty package names. | The dashboard shows a blank package heading and an empty entry in the 'No consumers' package list for such rows. |  |
| F-9 | minor | not challenged | design |  | `generator/build.py:182` | STATE_FILE (the api/state.csv path) is defined in build.py instead of generator/state.py, while the sibling BUILD_FILE lives in modules.py; __main__.py then reaches into build.STATE_FILE to lay out out/raw, leaking the state-file location through the assembler module. | none |  |
| F-10 | minor | not challenged | design |  | `generator/build.py:219` | assemble() re-parses codeowners_text and also takes both `published` and `gradle_texts`, although collect() already built Codeowners and derived published from the same texts; the pure assembler's input contract carries redundant, collect-derived data that can disagree (published keys vs gradle_texts keys). | none |  |
| F-11 | minor | not challenged | design |  | `generator/html.py:601` | The renderer infers three artifact states from a stringly-typed sentinel plus an empty-dict check (stability == STATE_UNKNOWN, else `not a\["packages"\]` means empty state.csv); the 'empty state.csv' case has no explicit field in the model that state.module_stability produces, so the contract between state.py and html.py is implicit. | none |  |
| F-12 | minor | not challenged | design |  | `generator/build.py:283` | The model published as out/data.json carries `tags`, `direct_pairs`, `transitive_pairs` and `state_totals` that html.py does not read (documented as added for acceptance checks), widening the data contract to serve tests and duplicating information already in artifacts\[\].consumers. | none |  |
| F-13 | minor | not challenged | design |  | `generator/html.py:695` | Redaction is applied at four layers (github.raw, build.collect extra catalogs, __main__ for data.json, html.render for HTML) with no single owner; render() redacts itself while data.json redaction lives in the CLI, so a new writer or caller of assemble gets inconsistent protection. | A future output path (or a library caller of assemble) could emit an unredacted API key into generated files. |  |
| F-14 | minor | not challenged | security |  | `generator/redact.py:4` | KEY_RE only matches the literal `key=` followed by \[A-Za-z0-9_-\]{8,}; keys with other characters (e.g. '.', '%', '~', '+') are only partly masked and `key: value`/`key = value` forms are not masked, yet this is the sole guard on fetched state.csv, data.json and dashboard.html. | A fetched file containing an API key in a slightly different shape could be written unmasked (or with its tail visible) into the shared dashboard output. |  |
| F-15 | minor | not challenged | performance |  | `generator/codeowners.py:458` | in_scope rebuilds set(self.team_paths(team)) (a full scan of all CODEOWNERS rules) on every call, then scans all rules again and runs a regex fullmatch per path prefix; build.in_scope_modules calls it once per maps/ module dir, so the work is modules x rules x depth with the team-pattern set recomputed each time. | a full regeneration spends extra seconds of CPU before any network fetch starts on a large CODEOWNERS file, with no change to the result. |  |
| F-16 | minor | not challenged | testability |  | `tests/test_acceptance.py:39` | setUp skips every M1-M5/S1/S3/S4/S5 acceptance test when out/data.json is absent, so the per-rule verify commands exit 0 with only skips on a fresh checkout; CleanCheckoutTest asserts that skip is intended, so no rule-level check can fail without a prior live run. | A regression in the generated dashboard data is reported as a passing test run unless someone ran the live generator first. |  |
| F-17 | minor | not challenged | testability |  | `generator/github.py:42` | The truncated-tree guard (raise RuntimeError when GitHub truncates the recursive tree) has no test; GithubTest only mocks tree responses with truncated False. | If the guard broke, a truncated tree would silently drop modules and consumers from the dashboard instead of failing the run. |  |
| F-18 | minor | not challenged | testability |  | `generator/build.py:141` | collect() passes github.raw's None (404) for CODEOWNERS straight into Codeowners(); the 404-to-None path and the missing-consumer-catalog RuntimeError in collect are untested (CollectTest only covers the happy path and state.csv filtering). | A missing CODEOWNERS or catalog would surface as an unhelpful AttributeError/crash, and nothing guards the intended message. |  |
| F-19 | minor | not challenged | testability |  | `tests/test_catalogs.py:52` | test_consumer_catalog_files_are_fixed re-types the CONSUMER_CATALOGS dict literal and compares it to itself, and CollectTest's raw mock returns CATALOGS\[repo\] for any path, so no test fails if the wrong catalog path is fetched. | A wrong catalog filename for a consumer would pass the tests and only fail (404 RuntimeError) in a live run. |  |
| F-20 | minor | not challenged | testability |  | `tests/test_acceptance.py:239` | The comment says the owner key 'reaches the model', but the mocked gh goes through github.raw, which redacts CODEOWNERS at fetch time, so the 'team-key=***' assertions in test_m5_injected_key_is_obfuscated pass even if output-stage redaction were removed; only the second test exercises that stage. | none |  |
| F-21 | minor | not challenged | testability |  | `tests/test_acceptance.py:29` | Acceptance assertions hardcode LATEST_STABLE 2.4.5, LATEST_RC 2.8.0-rc01 and 12-behind counts against live data, so the tests fail on the next go-sdk-android release even though the code is unchanged. | A routine SDK release turns the acceptance suite red with no code defect, eroding trust in failures. |  |
| F-22 | minor | not challenged | conventions |  | `docs/agentic/2026-10-06-mapvis-api-dashboard/light-design.md:41` | The tests/ bullet says test_acceptance.py 'fails with run python3 -m generator first when out/data.json is missing', but the committed tests call skipTest (Generated.setUp, CleanCheckoutTest), and the deviations table records no such change. | none |  |
| F-23 | minor | not challenged | conventions |  | `README.md:1` | The change adds a CLI (python3 -m generator --out out --extra-catalog ...) and a required live run before the acceptance tests, but README.md (repo root) has no usage or test instructions; the only record is in the design doc and module docstrings. | none |  |
| F-24 | minor | not challenged | docs-coherence |  | `docs/agentic/2026-10-06-mapvis-api-dashboard/light-design.md:31` | Program design says releases() runs `gh api --paginate "...releases?per_page=100"`, but github.releases() also passes `--jq ".\[\] \| {tag_name, draft}"` and parses line-delimited JSON; the doc and deviations table never mention the jq projection. | none |  |

## Refuted findings

None.

## Dimensions that produced no findings

- tools-verify

## Coverage

| Dimension | State | Reason | Model | Findings |
|-----------|-------|--------|-------|----------|
| correctness | reviewed |  | sonnet | 5 |
| contracts | reviewed |  | sonnet | 3 |
| design | reviewed |  | sonnet | 5 |
| security | reviewed |  | sonnet | 1 |
| performance | reviewed |  | sonnet | 1 |
| testability | reviewed |  | sonnet | 7 |
| conventions | reviewed |  | sonnet | 2 |
| docs-coherence | reviewed |  | sonnet | 1 |
| dependencies | not applicable | no dependency manifest or lockfile changed | none | 0 |
| infra | not applicable | no .tf or .tfvars file changed | none | 0 |
| tools-verify | reviewed |  | none | 0 |

**correctness** checked:
- generator/build.py assemble and collect: transitive loop, consumer totals, thread-pool fetch order
- generator/codeowners.py glob regex, prefix matching, last-match owner_of and in_scope
- generator/state.py parse_rows field split and package_of; generator/versions.py tag_key and behind
- generator/catalogs.py parse_catalog and pinned_version; generator/github.py 404 handling and truncated tree
- generator/modules.py api regex and accessor_to_path; generator/redact.py; __main__ raw file writing
- tests/test_acceptance.py and tests/test_build.py first half (diff lines 1-1334) for vacuous or wrong assertions
**contracts** checked:
- github.raw None-on-404 contract vs build.collect/published_modules/api_deps consumers of gradle_texts
- catalogs.pinned_version -> versions.tag_key ValueError contract vs build._version_row callers (real and extra catalogs)
- state.package_of/tally output keys vs html._packages and build unconsumed-package set
- codeowners/modules/state/redact/html call chains in assemble and __main__ (grep of tests for precedent of empty-catalog and None inputs: none found)
- transitive-pair loop in build.assemble against by_module/by_coord lookups and deps keys
**design** checked:
- generator/build.py assemble vs collect split and the inputs assemble takes
- generator/__main__.py, build.py, html.py, github.py redact call sites (grep redact)
- generator/state.py vs build.STATE_FILE and modules.BUILD_FILE constant placement
- generator/html.py model contract (stability sentinel, empty-state inference) against state.module_stability
- generator/codeowners.py, catalogs.py, versions.py public surface and cross-module imports
**security** checked:
- generator/github.py gh api subprocess calls (list args, no shell, constant org/repo/ref; stderr in RuntimeError)
- generator/redact.py KEY_RE and where redact() is applied (github.raw, build.collect extra catalogs, __main__ data.json, html.render)
- generator/html.py escaping: every interpolation goes through _e (html.escape); no hrefs, scripts or innerHTML
- generator/__main__.py and build.collect output path construction from tree module dirs and --extra-catalog paths; tomllib parsing in catalogs.py (no eval/pickle/yaml)
- grep for token/secret/eval/exec/shell=True across generator/ returned nothing risky; no new dependencies (stdlib only)
**performance** checked:
- generator/build.py collect(): ThreadPoolExecutor fetch fan-out, gradle-then-state.csv ordering, per-module gh subprocess count
- generator/codeowners.py in_scope/owner_of/_matches: per-call work over all rules and path prefixes, called once per maps/ module dir
- generator/build.py assemble(): set(published) rebuilt per module, consumer/transitive loops, state_totals loops
- generator/github.py + state.py + html.py + versions.py: pagination, tree fetch, row parsing, rendering loops, tag_key per tag
- grepped repo for other callers of in_scope to see if the hot path is wider than build.in_scope_modules (only build.py)
**testability** checked:
- tests/test_acceptance.py skip path and CleanCheckoutTest against the light-design verify commands
- tests/test_build.py CollectTest and GithubTest versus generator/github.py and build.collect error branches
- tests/test_acceptance.py InjectedKeyTest mock gh flow versus github.raw fetch-time redact
- tests/test_state.py and tests/test_catalogs.py assertions versus state.parse_rows and CONSUMER_CATALOGS
- grep for skipTest and truncated across tests/ and generator/ (only github.py:42 and one non-truncated mock)
**conventions** checked:
- light-design.md program-design bullets and deviations table against generator/*.py signatures and docstrings
- module docstrings and model-shape docs in html.py and build.py against assemble() output keys
- test naming and -k verify selectors in light-design against tests/test_acceptance.py test names
- sibling test modules for import and naming patterns (alias used for html in test_html.py vs other tests)
- README.md and repo root listing for generator usage docs (grep for python3 -m generator outside docs/agentic)
**docs-coherence** checked:
- light-design.md program-design bullets against generator/github.py, build.py, versions.py, state.py, catalogs.py, codeowners.py, modules.py, html.py, redact.py
- light-design.md deviation rows 1-7 against the code they describe (signatures, ref handling, empty state.csv, 8 workers, redaction points)
- N2/M5 verify commands and .gitignore entries against github.py contents and the diff's .gitignore
- README.md and ACCEPTANCE.md grep for generator/out/python claims; fixtures/ and reference/ file names exist
**tools-verify** checked:
- ran `time python3 -m generator --out out --extra-catalog old-version=fixtures/old-version.versions.toml && python3 -m unittest discover -s tests -v` in the checkout root; exit 0

## What each reviewer was given

Diff: `origin/main...HEAD` (ee1aef5d..cce91d53).

**correctness**:
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/.gitignore`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__main__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/github.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/versions.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_acceptance.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_versions.py`

**contracts**:
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/.gitignore`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__main__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/github.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/versions.py`

**design**:
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/.gitignore`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__main__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/github.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/versions.py`

**security**:
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/.gitignore`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__main__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/github.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/versions.py`

**performance**:
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/.gitignore`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__main__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/github.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/versions.py`

**testability**:
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/.gitignore`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__main__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/github.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/versions.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_acceptance.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_versions.py`

**conventions**:
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/.gitignore`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/__main__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/github.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/generator/versions.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/__init__.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_acceptance.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_build.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_catalogs.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_codeowners.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_html.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_modules.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_redact.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_state.py`
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/tests/test_versions.py`

**docs-coherence**:
- `/Users/golecszl/work/ai/android-sdk-api-aiworkshop/.gitignore`

Withheld (under `docs/agentic/2026-10-06-mapvis-api-dashboard/`):
- `docs/agentic/2026-10-06-mapvis-api-dashboard/light-design.md`

Sent to every dimension (matched no routing rule):
- `.gitignore`

## Fixes

### Round 1

- `cce91d53` fix(tests): skip out/ acceptance checks when no live run output exists

#### Covering tests

- Defect 1 (tests/test_acceptance.py: acceptance setUp fails when out/ is missing): `tests/test_acceptance.py` — `CleanCheckoutTest.test_acceptance_skips_when_outputs_missing` (points DATA/HTML at a missing out/ and asserts an AcceptanceTest is skipped with the run hint, no failures or errors). Also checked by hand: with out/ moved away, `python3 -m unittest discover -s tests` gives `Ran 89 tests ... OK (skipped=14)`.

#### Command

`time python3 -m generator --out out --extra-catalog old-version=fixtures/old-version.versions.toml && python3 -m unittest discover -s tests -v`

#### Output

```
wrote out/data.json, out/dashboard.html, 21 state.csv files under out/raw/

real	0m13.734s
user	0m3.320s
sys	0m2.106s
test_m1_artifact_direct_consumers_match_reference (test_acceptance.AcceptanceTest.test_m1_artifact_direct_consumers_match_reference) ... ok
test_m1_direct_pairs_match_reference (test_acceptance.AcceptanceTest.test_m1_direct_pairs_match_reference) ... ok
test_m2_docs_repos_only_in_docs_references (test_acceptance.AcceptanceTest.test_m2_docs_repos_only_in_docs_references) ... ok
test_m3_jpn_kor_styles_have_zero_direct_consumers (test_acceptance.AcceptanceTest.test_m3_jpn_kor_styles_have_zero_direct_consumers) ... ok
test_m4_baselines (test_acceptance.AcceptanceTest.test_m4_baselines) ... ok
test_m4_no_negative_counts_and_html_shows_both_baselines (test_acceptance.AcceptanceTest.test_m4_no_negative_counts_and_html_shows_both_baselines) ... ok
test_m4_old_version_fixture (test_acceptance.AcceptanceTest.test_m4_old_version_fixture) ... ok
test_m4_real_consumers_zero_behind_rc_and_ahead_of_stable (test_acceptance.AcceptanceTest.test_m4_real_consumers_zero_behind_rc_and_ahead_of_stable) ... ok
test_m5_outputs_contain_no_api_key (test_acceptance.AcceptanceTest.test_m5_outputs_contain_no_api_key) ... ok
test_s1_r2_navapp_transitive_via_duo_internal (test_acceptance.AcceptanceTest.test_s1_r2_navapp_transitive_via_duo_internal) ... ok
test_s1_transitive_never_duplicates_direct (test_acceptance.AcceptanceTest.test_s1_transitive_never_duplicates_direct) ... ok
test_s3_unconsumed_artifacts_and_packages_listed (test_acceptance.AcceptanceTest.test_s3_unconsumed_artifacts_and_packages_listed) ... ok
test_s4_internal_availability_column_and_total (test_acceptance.AcceptanceTest.test_s4_internal_availability_column_and_total) ... ok
test_s5_consumed_visualization_modules_state_unknown (test_acceptance.AcceptanceTest.test_s5_consumed_visualization_modules_state_unknown) ... ok
test_acceptance_skips_when_outputs_missing (test_acceptance.CleanCheckoutTest.test_acceptance_skips_when_outputs_missing) ... ok
test_m5_injected_key_is_obfuscated (test_acceptance.InjectedKeyTest.test_m5_injected_key_is_obfuscated) ... wrote /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpagd8mah5/out/data.json, /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpagd8mah5/out/dashboard.html, 1 state.csv files under /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpagd8mah5/out/raw/
ok
test_m5_output_stage_redacts_model (test_acceptance.InjectedKeyTest.test_m5_output_stage_redacts_model)
A key that reaches the model unredacted is still obfuscated in both outputs. ... wrote /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpdioumw7i/out/data.json, /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpdioumw7i/out/dashboard.html, 0 state.csv files under /var/folders/9j/jnc1xbcx23792qm3y90108mh0000gn/T/tmpdioumw7i/out/raw/
ok
test_artifacts_are_published_in_scope_modules (test_build.AssembleTest.test_artifacts_are_published_in_scope_modules) ... ok
test_baselines_and_consumer_versions (test_build.AssembleTest.test_baselines_and_consumer_versions) ... ok
test_catalog_without_mapvis_libraries_fails_loudly (test_build.AssembleTest.test_catalog_without_mapvis_libraries_fails_loudly) ... ok
test_direct_pairs_from_catalogs_deduped (test_build.AssembleTest.test_direct_pairs_from_catalogs_deduped) ... ok
test_docs_references_fixed_and_never_consumers (test_build.AssembleTest.test_docs_references_fixed_and_never_consumers) ... ok
test_extra_catalogs_kept_out_of_direct_pairs (test_build.AssembleTest.test_extra_catalogs_kept_out_of_direct_pairs) ... ok
test_in_scope_modules_from_codeowners_and_tree (test_build.AssembleTest.test_in_scope_modules_from_codeowners_and_tree) ... ok
test_model_is_json_serialisable (test_build.AssembleTest.test_model_is_json_serialisable) ... ok
test_published_modules_skip_unpublished (test_build.AssembleTest.test_published_modules_skip_unpublished) ... ok
test_stability_and_state_totals (test_build.AssembleTest.test_stability_and_state_totals) ... ok
test_totals_count_direct_and_transitive (test_build.AssembleTest.test_totals_count_direct_and_transitive) ... ok
test_transitive_does_not_duplicate_direct (test_build.AssembleTest.test_transitive_does_not_duplicate_direct) ... ok
test_transitive_one_level_via_artifact (test_build.AssembleTest.test_transitive_one_level_via_artifact) ... ok
test_unconsumed_artifacts_and_packages (test_build.AssembleTest.test_unconsumed_artifacts_and_packages) ... ok
test_unpublished_module_state_csv_not_fetched_nor_counted (test_build.CollectTest.test_unpublished_module_state_csv_not_fetched_nor_counted) ... ok
test_every_call_is_get_only (test_build.GithubTest.test_every_call_is_get_only) ... ok
test_raw_error_merely_containing_404_raises (test_build.GithubTest.test_raw_error_merely_containing_404_raises) ... ok
test_raw_is_redacted (test_build.GithubTest.test_raw_is_redacted) ... ok
test_raw_missing_file_returns_none (test_build.GithubTest.test_raw_missing_file_returns_none) ... ok
test_raw_other_error_raises (test_build.GithubTest.test_raw_other_error_raises) ... ok
test_consumer_catalog_files_are_fixed (test_catalogs.CatalogTest.test_consumer_catalog_files_are_fixed) ... ok
test_fixture_resolves_gosdk_for_two_maps_libraries (test_catalogs.CatalogTest.test_fixture_resolves_gosdk_for_two_maps_libraries) ... ok
test_no_space_inline_table_and_literal_version (test_catalogs.CatalogTest.test_no_space_inline_table_and_literal_version) ... ok
test_non_maps_groups_dropped_and_aliases_deduped (test_catalogs.CatalogTest.test_non_maps_groups_dropped_and_aliases_deduped) ... ok
test_pinned_version_is_lowest_resolved (test_catalogs.CatalogTest.test_pinned_version_is_lowest_resolved) ... ok
test_commented_lines_and_trailing_comments_ignored (test_codeowners.CodeownersTest.test_commented_lines_and_trailing_comments_ignored) ... ok
test_double_star_globs_do_not_match_the_module_directory_itself (test_codeowners.CodeownersTest.test_double_star_globs_do_not_match_the_module_directory_itself) ... ok
test_in_scope_when_any_team_pattern_matches (test_codeowners.CodeownersTest.test_in_scope_when_any_team_pattern_matches) ... ok
test_last_match_wins_for_visualization_routing (test_codeowners.CodeownersTest.test_last_match_wins_for_visualization_routing) ... ok
test_more_specific_later_rule_overrides (test_codeowners.CodeownersTest.test_more_specific_later_rule_overrides) ... ok
test_multiple_owners_are_all_reported (test_codeowners.CodeownersTest.test_multiple_owners_are_all_reported) ... ok
test_team_paths_lists_patterns_naming_the_team (test_codeowners.CodeownersTest.test_team_paths_lists_patterns_naming_the_team) ... ok
test_unanchored_glob_matches_anywhere (test_codeowners.CodeownersTest.test_unanchored_glob_matches_anywhere) ... ok
test_unowned_path (test_codeowners.CodeownersTest.test_unowned_path) ... ok
test_consumer_versions_section (test_html.RenderTest.test_consumer_versions_section) ... ok
test_docs_references_section_lists_both_repos (test_html.RenderTest.test_docs_references_section_lists_both_repos) ... ok
test_empty_state_csv_is_not_state_unknown (test_html.RenderTest.test_empty_state_csv_is_not_state_unknown) ... ok
test_extra_catalogs_section_when_present (test_html.RenderTest.test_extra_catalogs_section_when_present) ... ok
test_grouped_by_package (test_html.RenderTest.test_grouped_by_package) ... ok
test_no_consumers_section (test_html.RenderTest.test_no_consumers_section) ... ok
test_no_key_in_output (test_html.RenderTest.test_no_key_in_output) ... ok
test_self_contained_document (test_html.RenderTest.test_self_contained_document) ... ok
test_stability_totals_one_column_per_state (test_html.RenderTest.test_stability_totals_one_column_per_state) ... ok
test_state_columns_include_internal_availability (test_html.RenderTest.test_state_columns_include_internal_availability) ... ok
test_state_unknown_shown (test_html.RenderTest.test_state_unknown_shown) ... ok
test_text_is_escaped (test_html.RenderTest.test_text_is_escaped) ... ok
test_transitive_consumer_shown_via_artifact (test_html.RenderTest.test_transitive_consumer_shown_via_artifact) ... ok
test_accessor_camel_case_to_kebab_path (test_modules.ApiDepsTest.test_accessor_camel_case_to_kebab_path) ... ok
test_indented_kmp_source_set_api_deps_found (test_modules.ApiDepsTest.test_indented_kmp_source_set_api_deps_found) ... ok
test_top_level_api_deps_found_implementation_ignored_non_maps_dropped (test_modules.ApiDepsTest.test_top_level_api_deps_found_implementation_ignored_non_maps_dropped) ... ok
test_directories_under_maps_with_build_file (test_modules.ModuleDirsTest.test_directories_under_maps_with_build_file) ... ok
test_coordinate_from_extra_lines (test_modules.ParseModuleTest.test_coordinate_from_extra_lines) ... ok
test_coordinate_uses_group_id_not_directory (test_modules.ParseModuleTest.test_coordinate_uses_group_id_not_directory) ... ok
test_module_without_artifact_id_is_skipped (test_modules.ParseModuleTest.test_module_without_artifact_id_is_skipped) ... ok
test_every_occurrence_obfuscated (test_redact.RedactTest.test_every_occurrence_obfuscated) ... ok
test_key_in_url_keeps_surrounding_text (test_redact.RedactTest.test_key_in_url_keeps_surrounding_text) ... ok
test_key_token_obfuscated (test_redact.RedactTest.test_key_token_obfuscated) ... ok
test_short_values_left_alone (test_redact.RedactTest.test_short_values_left_alone) ... ok
test_class_and_member_rows (test_state.PackageOfTest.test_class_and_member_rows) ... ok
test_file_facade_row (test_state.PackageOfTest.test_file_facade_row) ... ok
test_lowercase_inside_parentheses_ignored (test_state.PackageOfTest.test_lowercase_inside_parentheses_ignored) ... ok
test_semicolon_split_keeps_commas_in_names (test_state.ParseRowsTest.test_semicolon_split_keeps_commas_in_names) ... ok
test_missing_state_csv_is_state_unknown (test_state.TallyTest.test_missing_state_csv_is_state_unknown) ... ok
test_module_with_state_csv (test_state.TallyTest.test_module_with_state_csv) ... ok
test_tally_per_package_and_state_with_internal_availability_separate (test_state.TallyTest.test_tally_per_package_and_state_with_internal_availability_separate) ... ok
test_old_version_fixture_is_12_behind_latest_rc (test_versions.BehindTest.test_old_version_fixture_is_12_behind_latest_rc) ... ok
test_older_pin_counts_tags_up_to_baseline (test_versions.BehindTest.test_older_pin_counts_tags_up_to_baseline) ... ok
test_pin_equal_to_baseline_is_zero (test_versions.BehindTest.test_pin_equal_to_baseline_is_zero) ... ok
test_pin_newer_than_stable_is_ahead (test_versions.BehindTest.test_pin_newer_than_stable_is_ahead) ... ok
test_drops_drafts_and_dev_tags (test_versions.ReleaseTagsTest.test_drops_drafts_and_dev_tags) ... ok
test_latest_rc_is_highest_semver_rc (test_versions.ReleaseTagsTest.test_latest_rc_is_highest_semver_rc) ... ok
test_rc_sorts_before_stable_of_same_version (test_versions.ReleaseTagsTest.test_rc_sorts_before_stable_of_same_version) ... ok

----------------------------------------------------------------------
Ran 89 tests in 0.031s

OK
```

## Gaps

- Withheld from every read set: `docs/agentic/2026-10-06-mapvis-api-dashboard/light-design.md` — they are part of the change, so they remain visible in the diff every reviewer reads.
