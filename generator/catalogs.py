"""Gradle version catalogs: MapVis SDK libraries a consumer declares and the version it pins."""
import tomllib

from generator.versions import tag_key

MAPS_GROUPS = ("com.tomtom.sdk.maps", "com.tomtom.sdk.maps.visualization")

# Fixed catalog file per consumer repo (D-9).
CONSUMER_CATALOGS = {
    "oneapp-android": "gradle/libs.versions.toml",
    "navapp-automotive": "gradle/gosdk-libs.versions.toml",
    "r2-navapp": "gradle/gosdk-libs.versions.toml",
}


def _resolve(version, versions):
    if isinstance(version, str):
        return version
    if isinstance(version, dict) and "ref" in version:
        return versions.get(version["ref"])
    return None


def parse_catalog(text):
    """{groupId:artifactId: resolved version} for MapVis libraries, deduped by module."""
    data = tomllib.loads(text)
    versions = data.get("versions", {})
    libs = {}
    for lib in data.get("libraries", {}).values():
        module = lib.get("module") if isinstance(lib, dict) else None
        if not module or module.split(":", 1)[0] not in MAPS_GROUPS:
            continue
        libs.setdefault(module, _resolve(lib.get("version"), versions))
    return libs


def pinned_version(libs):
    """Lowest resolved version among the libraries, or None when there are none."""
    resolved = [v for v in libs.values() if v]
    return min(resolved, key=tag_key) if resolved else None
