# Acceptance criteria — MapVis Android SDK API Dashboard

Pass/fail rules the implementation must meet. Each rule is checked by an automated test or a
scripted comparison — never by reading the code.

## Scope

- **APIs:** modules owned by `@tomtom-internal/lp-mapvis-mapdisplaysdk-android` in
  [`go-sdk-android/CODEOWNERS`](https://github.com/tomtom-internal/go-sdk-android/blob/master/CODEOWNERS),
  with stability read from each module's `api/state.csv`.
- **Consumers:** `oneapp-android`, `navapp-automotive`, `r2-navapp` — read from their Gradle
  version catalogs.
- **Docs references (never consumers):** `mapdisplay-for-unity`, `devportal-documentation`.
- **Out of scope:** `go-sdk-ios`, `oneapp-ios`, usage (call) counts, Map Display REST endpoints.
- **Versioning:** only `go-sdk-android` release tags. Latest stable = GitHub release marked
  "latest" (production flavours); latest RC = newest `-rcNN` tag.
- **Grouping:** by package.

## Must

| # | Rule | Evidence |
|---|---|---|
| M1 | Direct consumer→artifact pairs exactly match `reference/direct-consumers.csv` (26 pairs): none missing, none extra. | Test diffs generated data against the CSV. |
| M2 | Docs repos appear only in a "docs references" section, never as consumers. | Test asserts both repos absent from consumer data. |
| M3 | Artifacts no consumer declares (e.g. `map-display-premium-jpn-styles`, `-kor-styles`) show zero direct consumers. | Test on generated data. |
| M4 | Each consumer shows its pinned SDK version compared with two baselines: **latest stable** (the GitHub release marked "latest" — production flavours, `2.4.5` on 2026-10-06) and **latest RC** (newest `-rcNN` tag — `2.8.0-rc01` on 2026-10-06), and how many releases behind each it is. A consumer newer than latest stable shows "ahead of stable", never a negative count. | `fixtures/old-version.versions.toml` (pinned `2.6.0`) shows > 0 behind latest RC and "ahead of stable"; the three real consumers show 0 behind latest RC. |
| M5 | Output never contains an API key; any key found in source is obfuscated. | Test scans generated HTML for key patterns (e.g. `key=` followed by a token). |

## Should

| # | Rule | Evidence |
|---|---|---|
| S1 | One level of transitive dependencies via `api(...)` in `go-sdk-android` `build.gradle.kts`, shown as "via `<artifact>`" and counted toward consumer totals. | `r2-navapp` lists `map-display-common`, `-standard`, `-premium` as transitive via `map-display-duo-internal`. |
| S2 | Alpha/Beta symbols per package, with the date they entered that state (git history of `state.csv`). | Spot-check 3 entries against `git log` by hand. |
| S3 | Packages/artifacts with no consumer (direct or transitive) listed. | Test on generated data. |
| S4 | `INTERNAL_AVAILABILITY` (Production-grade, never GA) shown as its own category. | Count matches `state.csv` tally. |
| S5 | Consumed modules with no `state.csv` (`visualization:navigation`, `:poi`, `:range`) shown as "state unknown" — never guessed, never dropped. | Test on generated data. |

## Non-functional

| # | Rule | Evidence |
|---|---|---|
| N1 | Full regeneration completes in < 30 min within GitHub API rate limits. | Timed run. |
| N2 | Read-only against all other repos; all code lives in this repo. | No writes outside this repo. |

## Stretch

- Weekly scheduled refresh (needs a PAT / GitHub App with org read access).

## Open decisions ⚠️

- **Reference snapshot date.** `reference/direct-consumers.csv` was confirmed on 2026-10-06; if
  consumers change their catalogs, re-confirm it before the test run.
