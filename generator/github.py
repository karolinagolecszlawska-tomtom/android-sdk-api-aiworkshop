"""Read-only GitHub access through `gh api` (GET requests only, N2).

Every call reuses the user's existing `gh` authentication. Fetched file contents are
redacted (M5) before anything else sees them.
"""
import json
import subprocess

from generator.redact import redact

ORG = "tomtom-internal"
SDK_REPO = "go-sdk-android"
SDK_BRANCH = "master"
RAW_ACCEPT = "Accept: application/vnd.github.raw"


def _gh(endpoint, *extra):
    """Run `gh api <endpoint>` (implicit GET); returns the CompletedProcess."""
    return subprocess.run(["gh", "api", endpoint, *extra],
                          capture_output=True, text=True, check=False)


def _check(proc, endpoint):
    if proc.returncode != 0:
        raise RuntimeError(f"gh api {endpoint} failed: {proc.stderr.strip()}")
    return proc.stdout


def raw(repo, path, ref=None):
    """Redacted contents of `path` in `repo` (default branch when `ref` is None); None on 404."""
    endpoint = f"repos/{ORG}/{repo}/contents/{path}" + (f"?ref={ref}" if ref else "")
    proc = _gh(endpoint, "-H", RAW_ACCEPT)
    if proc.returncode != 0 and "HTTP 404" in proc.stderr:
        return None
    return redact(_check(proc, endpoint))


def tree(repo, branch):
    """All blob/tree paths of `repo` at `branch` (recursive)."""
    endpoint = f"repos/{ORG}/{repo}/git/trees/{branch}?recursive=1"
    data = json.loads(_check(_gh(endpoint), endpoint))
    if data.get("truncated"):
        raise RuntimeError(f"tree of {repo}@{branch} is truncated")
    return [entry["path"] for entry in data["tree"]]


def releases():
    """Every go-sdk-android release (drafts included; filtering happens in versions.py)."""
    endpoint = f"repos/{ORG}/{SDK_REPO}/releases?per_page=100"
    out = _check(_gh(endpoint, "--paginate", "--jq", ".[] | {tag_name, draft}"), endpoint)
    return [json.loads(line) for line in out.splitlines() if line.strip()]


def latest_release():
    """Tag of the go-sdk-android release marked "latest"."""
    endpoint = f"repos/{ORG}/{SDK_REPO}/releases/latest"
    return _check(_gh(endpoint, "--jq", ".tag_name"), endpoint).strip()
