"""Renders the self-contained dashboard.html from the build model.

Model keys read here (produced by generator/build.py):
  baselines          {"stable": tag, "rc": tag}
  artifacts          [{"coordinate", "module", "owner", "stability" (None | "state unknown"),
                       "packages": {package: {state: count}},
                       "consumers": [{"repo", "via" (None | via-artifact coordinate)}],
                       "consumer_total"}]
  consumer_versions  [{"repo", "pinned", "behind_stable", "behind_rc"}]  (int or "ahead of …")
  unconsumed         {"artifacts": [coordinate], "packages": [package]}
  docs_references    [repo name]
  extra_consumers    [{"name", "pinned", "behind_stable", "behind_rc", "artifacts": [coordinate]}]
"""
from html import escape

from generator.redact import redact
from generator.state import STATE_UNKNOWN

STATE_ORDER = ["GA", "BETA", "ALPHA", "EXPERIMENTAL", "DEPRECATED", "INTERNAL",
               "INTERNAL_AVAILABILITY"]
UNKNOWN_GROUP = "Packages unknown (no state.csv)"

CSS = """
:root { color-scheme: light dark; --fg: #1d1d1f; --bg: #ffffff; --muted: #6e6e73;
        --line: #d2d2d7; --head: #f5f5f7; }
@media (prefers-color-scheme: dark) {
  :root { --fg: #f5f5f7; --bg: #161617; --muted: #a1a1a6; --line: #3a3a3c; --head: #232325; }
}
body { font: 14px/1.45 system-ui, sans-serif; color: var(--fg); background: var(--bg);
       margin: 0 auto; padding: 16px; max-width: 1200px; }
h1 { font-size: 22px; } h2 { font-size: 18px; margin-top: 32px; } h3 { font-size: 15px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 16px; display: block;
        overflow-x: auto; }
th, td { border: 1px solid var(--line); padding: 4px 8px; text-align: left; vertical-align: top; }
th { background: var(--head); }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
.muted { color: var(--muted); }
code { font-size: 13px; }
"""


def _e(value):
    return escape(str(value))


def _artifact_id(coordinate):
    return coordinate.split(":", 1)[-1]


def _state_columns(artifacts):
    present = {s for a in artifacts for counts in a["packages"].values() for s in counts}
    return [s for s in STATE_ORDER if s in present] + sorted(present - set(STATE_ORDER))


def _consumers_cell(artifact):
    items = []
    for c in artifact["consumers"]:
        if c.get("via"):
            items.append(f"{_e(c['repo'])} via <code>{_e(_artifact_id(c['via']))}</code>")
        else:
            items.append(_e(c["repo"]))
    return "<br>".join(items) if items else '<span class="muted">none</span>'


def _packages(artifacts):
    groups = {}
    for a in artifacts:
        if a.get("stability") == STATE_UNKNOWN or not a["packages"]:
            groups.setdefault(UNKNOWN_GROUP, []).append((a, None))
            continue
        for package, counts in a["packages"].items():
            groups.setdefault(package, []).append((a, counts))
    return sorted(groups.items(), key=lambda kv: (kv[0] == UNKNOWN_GROUP, kv[0]))


def _package_sections(model):
    columns = _state_columns(model["artifacts"])
    head = ("<tr><th>Artifact</th><th>Owner</th>"
            + "".join(f"<th>{_e(s)}</th>" for s in columns)
            + "<th>Consumers</th><th>Total</th></tr>")
    out = []
    for package, rows in _packages(model["artifacts"]):
        out.append(f"<h3>{_e(package)}</h3><table>{head}")
        for artifact, counts in rows:
            if counts is None:
                states = f'<td colspan="{max(len(columns), 1)}">{_e(STATE_UNKNOWN)}</td>'
            else:
                states = "".join(f'<td class="num">{counts.get(s, 0)}</td>' for s in columns)
            out.append(
                f"<tr><td><code>{_e(artifact['coordinate'])}</code></td>"
                f"<td>{_e(artifact.get('owner') or '')}</td>{states}"
                f"<td>{_consumers_cell(artifact)}</td>"
                f"<td class=\"num\">{_e(artifact.get('consumer_total', 0))}</td></tr>")
        out.append("</table>")
    return "".join(out)


def _versions_table(rows, name_key, baselines, extra_column=None):
    head = (f"<tr><th>Consumer</th><th>Pinned</th>"
            f"<th>Behind latest stable ({_e(baselines['stable'])})</th>"
            f"<th>Behind latest RC ({_e(baselines['rc'])})</th>"
            + (f"<th>{_e(extra_column[0])}</th>" if extra_column else "") + "</tr>")
    body = "".join(
        f"<tr><td>{_e(r[name_key])}</td><td>{_e(r['pinned'])}</td>"
        f"<td>{_e(r['behind_stable'])}</td><td>{_e(r['behind_rc'])}</td>"
        + (f"<td>{extra_column[1](r)}</td>" if extra_column else "") + "</tr>"
        for r in rows)
    return f"<table>{head}{body}</table>"


def _list(items):
    if not items:
        return '<p class="muted">None.</p>'
    return "<ul>" + "".join(f"<li><code>{_e(i)}</code></li>" for i in items) + "</ul>"


def _section(title, body):
    return f"<section>\n<h2>{_e(title)}</h2>{body}</section>\n"


def render(model):
    """Full dashboard HTML for `model`, with any API key redacted."""
    baselines = model["baselines"]
    unconsumed = model.get("unconsumed", {"artifacts": [], "packages": []})
    parts = [
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>MapVis API Dashboard</title>",
        f"<style>{CSS}</style></head><body>",
        "<h1>MapVis Android SDK API dashboard</h1>",
        f"<p class=\"muted\">Latest stable {_e(baselines['stable'])} · "
        f"latest RC {_e(baselines['rc'])}</p>",
        _section("Packages", _package_sections(model)),
        _section("Consumer versions",
                 _versions_table(model.get("consumer_versions", []), "repo", baselines)),
        _section("No consumers",
                 "<h3>Artifacts</h3>" + _list(unconsumed.get("artifacts", []))
                 + "<h3>Packages</h3>" + _list(unconsumed.get("packages", []))),
        _section("Docs references",
                 "<p class=\"muted\">Documentation repos, never counted as consumers.</p>"
                 "<ul>" + "".join(f"<li>{_e(r)}</li>" for r in model.get("docs_references", []))
                 + "</ul>"),
    ]
    extra = model.get("extra_consumers") or []
    if extra:
        parts.append(_section("Extra catalogs", _versions_table(
            extra, "name", baselines,
            ("Artifacts", lambda r: "<br>".join(f"<code>{_e(a)}</code>"
                                                for a in r.get("artifacts", []))))))
    parts.append("</body></html>\n")
    return redact("".join(parts))
