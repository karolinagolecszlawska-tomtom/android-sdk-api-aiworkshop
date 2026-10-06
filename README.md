# android-sdk-api-aiworkshop

**MapVis Android SDK API Dashboard** — workshop task (TomTom Agentic Coding Workshop, Level 3).

- **What:** Shows which downstream Android apps use each MapVis SDK artifact (direct and transitive), its packages' stability (Alpha/Beta/GA/Internal-availability), and how many go-sdk-android releases behind each app is.
- **Build:** Generator script reading go-sdk-android `state.csv` and `build.gradle.kts` files plus the version catalogs of oneapp-android, navapp-automotive and r2-navapp; outputs static HTML grouped by package.
- **Size:** ~10 days manual, ~1 day agent.
- **Validate:** see [ACCEPTANCE.md](ACCEPTANCE.md) and [reference/direct-consumers.csv](reference/direct-consumers.csv).
