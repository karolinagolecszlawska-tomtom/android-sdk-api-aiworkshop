"""go-sdk-android Gradle modules: published coordinates and api(projects.…) dependencies."""
import re

_ARTIFACT_RE = re.compile(r'val\s+artifactId\s+by\s+extra\(\s*"([^"]+)"\s*\)')
_GROUP_RE = re.compile(r'val\s+groupId\s+by\s+extra\(\s*"([^"]+)"\s*\)')
_API_RE = re.compile(r"^\s*api\(projects\.([\w.]+)\)", re.MULTILINE)
BUILD_FILE = "build.gradle.kts"


def module_dirs(tree_paths, root="maps"):
    """Directories under `root` that hold a build.gradle.kts, sorted."""
    suffix = "/" + BUILD_FILE
    return sorted(p[: -len(suffix)] for p in tree_paths
                  if p.startswith(root + "/") and p.endswith(suffix))


def parse_module(gradle_text):
    """`groupId:artifactId` coordinate a build file publishes, or None when unpublished."""
    artifact, group = _ARTIFACT_RE.search(gradle_text), _GROUP_RE.search(gradle_text)
    if not (artifact and group):
        return None
    return f"{group.group(1)}:{artifact.group(1)}"


def accessor_to_path(accessor):
    """`maps.mapDisplayCommon` -> `maps/map-display-common`."""
    return "/".join(re.sub(r"(?<!^)([A-Z])", r"-\1", seg).lower()
                    for seg in accessor.split("."))


def api_deps(gradle_text, in_scope):
    """Module paths of `api(projects.…)` dependencies that are in `in_scope`, in file order."""
    deps = []
    for accessor in _API_RE.findall(gradle_text):
        path = accessor_to_path(accessor)
        if path in in_scope and path not in deps:
            deps.append(path)
    return deps
