"""api/state.csv parsing: rows, package derivation and per-package state tallies."""

STATE_UNKNOWN = "state unknown"
FIELDS = ("module_name", "domain", "name", "type", "state", "hasDoc", "flavor")


def parse_rows(text):
    """Rows of a `;`-separated state.csv as dicts; header and blank lines skipped."""
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("module_name;"):
            continue
        parts = line.split(";")
        if len(parts) < len(FIELDS):
            continue
        # Keep any stray ';' inside the name: first two and last four fields are fixed.
        fields = parts[:2] + [";".join(parts[2:-4])] + parts[-4:]
        rows.append(dict(zip(FIELDS, fields)))
    return rows


def package_of(name):
    """Leading lowercase dot-segments of `name` before the first `(`."""
    segments = []
    for seg in name.split("(", 1)[0].split("."):
        if not seg[:1].islower():
            break
        segments.append(seg)
    return ".".join(segments)


def tally(text):
    """{package: {state: row count}} over every row, one key per state value present."""
    result = {}
    for row in parse_rows(text):
        counts = result.setdefault(package_of(row["name"]), {})
        counts[row["state"]] = counts.get(row["state"], 0) + 1
    return result


def module_stability(text):
    """Stability of one module: tallies when state.csv exists, else `state unknown`."""
    if text is None:
        return {"stability": STATE_UNKNOWN, "packages": {}}
    return {"stability": None, "packages": tally(text)}
