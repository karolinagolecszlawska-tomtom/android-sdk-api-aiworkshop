"""go-sdk-android release tags: filtering, semver ordering and "releases behind" counts."""
import re

TAG_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-rc(\d+))?$")


def tag_key(tag):
    """Sort key: X.Y.Z-rcNN sorts before X.Y.Z. Raises ValueError for non-release tags."""
    m = TAG_RE.match(tag) if isinstance(tag, str) else None
    if not m:
        raise ValueError(f"not a release tag: {tag!r}")
    major, minor, patch, rc = m.groups()
    base = (int(major), int(minor), int(patch))
    return base + ((0, int(rc)) if rc is not None else (1, 0))


def is_rc(tag):
    m = TAG_RE.match(tag)
    return bool(m and m.group(4) is not None)


def release_tags(releases):
    """Non-draft release tags matching X.Y.Z or X.Y.Z-rcNN, sorted semver-style."""
    tags = {r["tag_name"] for r in releases
            if not r.get("draft") and TAG_RE.match(r["tag_name"])}
    return sorted(tags, key=tag_key)


def latest_rc(tags):
    """Highest-semver -rcNN tag (not the newest by date)."""
    rcs = [t for t in tags if is_rc(t)]
    return max(rcs, key=tag_key) if rcs else None


def behind(pin, baseline, tags, label):
    """Count of tags t with pin < t <= baseline, or "ahead of <label>" when pin > baseline."""
    pin_key, base_key = tag_key(pin), tag_key(baseline)
    if pin_key > base_key:
        return f"ahead of {label}"
    return sum(1 for t in tags if pin_key < tag_key(t) <= base_key)
