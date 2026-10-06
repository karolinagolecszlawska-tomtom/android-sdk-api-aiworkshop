"""Assembles the dashboard model (see generator/html.py for its shape) from fetched inputs.

`assemble(...)` is pure: it takes file contents already fetched (and redacted) and returns
the model. `collect(...)` fetches those inputs live through generator/github.py.
"""
from concurrent.futures import ThreadPoolExecutor

from generator import catalogs as catalogs_mod
from generator import github
from generator.codeowners import Codeowners
from generator.modules import BUILD_FILE, api_deps, module_dirs, parse_module
from generator.redact import redact
from generator.state import module_stability
from generator.versions import behind, latest_rc, release_tags

DOCS_REFERENCES = ["mapdisplay-for-unity", "devportal-documentation"]
STATE_FILE = "api/state.csv"


def _version_row(pin, baselines, tags):
    """Raises ValueError when the pin or a baseline is not a release tag."""
    return {"pinned": pin,
            "behind_stable": behind(pin, baselines["stable"], tags, "stable"),
            "behind_rc": behind(pin, baselines["rc"], tags, "RC")}


def in_scope_modules(owners, tree_paths):
    """Module dirs under maps/ that a CODEOWNERS pattern naming the team covers (D-3)."""
    return [d for d in module_dirs(tree_paths) if owners.in_scope(d)]


def published_modules(gradle_texts):
    """{module dir: coordinate} for the modules whose build file publishes one (D-12)."""
    published = {}
    for module in sorted(gradle_texts):
        coordinate = parse_module(gradle_texts[module])
        if coordinate is not None:
            published[module] = coordinate
    return published


def assemble(*, codeowners_text, published, gradle_texts, state_texts, catalogs, releases,
             latest_tag, extra_catalogs=None):
    """Dashboard model.

    published:      {module dir: coordinate} of the in-scope published modules
    gradle_texts:   {module dir: build.gradle.kts text}
    state_texts:    {module dir: api/state.csv text, or None when the module has none}
    catalogs:       {consumer repo: version catalog text}
    releases:       [{"tag_name", "draft"}] of go-sdk-android
    latest_tag:     tag of the release marked "latest"
    extra_catalogs: {name: catalog text}, shown separately, never as consumers (D-6)
    """
    owners = Codeowners(codeowners_text)

    artifacts, by_module = [], {}
    for module in sorted(published):
        stability = module_stability(state_texts.get(module))
        artifact = {"coordinate": published[module], "module": module,
                    "owner": owners.owner_of(module), "stability": stability["stability"],
                    "packages": stability["packages"], "consumers": [], "consumer_total": 0}
        artifacts.append(artifact)
        by_module[module] = artifact
    deps = {m: api_deps(gradle_texts.get(m, ""), set(published)) for m in by_module}
    by_coord = {a["coordinate"]: a for a in artifacts}

    tags = release_tags(releases)
    baselines = {"stable": latest_tag, "rc": latest_rc(tags)}

    direct_pairs, consumer_versions = [], []
    direct = {}  # repo -> set of coordinates
    for repo, text in catalogs.items():
        libs = catalogs_mod.parse_catalog(text)
        direct[repo] = set(libs)
        direct_pairs += [{"repo": repo, "artifact": c, "version": v} for c, v in libs.items()]
        consumer_versions.append(
            {"repo": repo, **_version_row(catalogs_mod.pinned_version(libs), baselines, tags)})

    # One level of transitive dependencies through api(projects.…) (S1).
    transitive_pairs, seen = [], set()
    for repo, coords in direct.items():
        for coord in sorted(coords):
            source = by_coord.get(coord)
            if source is None:
                continue
            for dep in deps[source["module"]]:
                target = by_module[dep]["coordinate"]
                if target in coords or (repo, target) in seen:
                    continue
                seen.add((repo, target))
                transitive_pairs.append({"repo": repo, "artifact": target, "via": coord})

    for p in direct_pairs:
        if p["artifact"] in by_coord:
            by_coord[p["artifact"]]["consumers"].append({"repo": p["repo"], "via": None})
    for p in transitive_pairs:
        by_coord[p["artifact"]]["consumers"].append({"repo": p["repo"], "via": p["via"]})
    for a in artifacts:
        a["consumer_total"] = len({c["repo"] for c in a["consumers"]})

    consumed_packages = {pkg for a in artifacts if a["consumer_total"] for pkg in a["packages"]}
    all_packages = {pkg for a in artifacts for pkg in a["packages"]}
    state_totals = {}
    for a in artifacts:
        for counts in a["packages"].values():
            for state, n in counts.items():
                state_totals[state] = state_totals.get(state, 0) + n

    extra_consumers = []
    for name, text in (extra_catalogs or {}).items():
        libs = catalogs_mod.parse_catalog(text)
        extra_consumers.append({"name": name, "artifacts": sorted(libs),
                                **_version_row(catalogs_mod.pinned_version(libs), baselines,
                                               tags)})

    return {
        "baselines": baselines,
        "tags": tags,
        "artifacts": artifacts,
        "direct_pairs": direct_pairs,
        "transitive_pairs": transitive_pairs,
        "consumer_versions": consumer_versions,
        "unconsumed": {
            "artifacts": [a["coordinate"] for a in artifacts if not a["consumer_total"]],
            "packages": sorted(all_packages - consumed_packages),
        },
        "state_totals": state_totals,
        "docs_references": list(DOCS_REFERENCES),
        "extra_consumers": extra_consumers,
    }


def collect(extra_catalog_paths=None, workers=8):
    """Fetch every input live (read-only) and return (assemble kwargs, raw state files).

    raw state files: {module dir: state.csv text} for the modules that have one.
    """
    repo, ref = github.SDK_REPO, github.SDK_BRANCH
    tree_paths = github.tree(repo, ref)
    paths = set(tree_paths)
    owners_text = github.raw(repo, "CODEOWNERS", ref=ref)
    modules = in_scope_modules(Codeowners(owners_text), tree_paths)

    def fetch(path):
        return github.raw(repo, path, ref=ref)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        cat_f = {r: pool.submit(github.raw, r, p)
                 for r, p in catalogs_mod.CONSUMER_CATALOGS.items()}
        rel_f = pool.submit(github.releases)
        latest_f = pool.submit(github.latest_release)
        # Build files first: state.csv is fetched only for published modules (D-12).
        gradle_f = {m: pool.submit(fetch, f"{m}/{BUILD_FILE}") for m in modules}
        gradle_texts = {m: f.result() for m, f in gradle_f.items()}
        published = published_modules(gradle_texts)
        state_f = {m: pool.submit(fetch, f"{m}/{STATE_FILE}") for m in published
                   if f"{m}/{STATE_FILE}" in paths}
        state_texts = {m: (state_f[m].result() if m in state_f else None) for m in published}
        cats = {}
        for r, f in cat_f.items():
            text = f.result()
            if text is None:
                raise RuntimeError(f"catalog {catalogs_mod.CONSUMER_CATALOGS[r]} missing in {r}")
            cats[r] = text
        releases, latest = rel_f.result(), latest_f.result()

    extra = {}
    for name, path in (extra_catalog_paths or {}).items():
        with open(path, encoding="utf-8") as fh:
            extra[name] = redact(fh.read())

    kwargs = dict(codeowners_text=owners_text, published=published, gradle_texts=gradle_texts,
                  state_texts=state_texts, catalogs=cats, releases=releases, latest_tag=latest,
                  extra_catalogs=extra)
    raw_states = {m: t for m, t in state_texts.items() if t is not None}
    return kwargs, raw_states
