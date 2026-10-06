"""CODEOWNERS parsing: team patterns, last-match-wins ownership (gitignore-style globs)."""
import re

TEAM = "@tomtom-internal/lp-mapvis-mapdisplaysdk-android"


def _glob_to_regex(pattern):
    body = pattern.strip("/")
    anchored = pattern.startswith("/") or "/" in body
    out, i = [], 0
    while i < len(body):
        if body.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif body.startswith("**", i):
            out.append(".*")
            i += 2
        elif body[i] == "*":
            out.append("[^/]*")
            i += 1
        elif body[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(body[i]))
            i += 1
    prefix = "" if anchored else "(?:.*/)?"
    return re.compile(prefix + "".join(out))


def _short(owner):
    return owner.lstrip("@").split("/", 1)[-1]


class Codeowners:
    def __init__(self, text):
        self.rules = []  # (pattern, regex, [owners])
        for line in text.splitlines():
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            pattern, *owners = line.split()
            self.rules.append((pattern, _glob_to_regex(pattern), owners))

    def team_paths(self, team=TEAM):
        """Patterns whose owners include `team`, in file order."""
        return [p for p, _, owners in self.rules if team in owners]

    @staticmethod
    def _matches(regex, path):
        parts = path.strip("/").split("/")
        # A pattern matching a directory also covers everything beneath it.
        return any(regex.fullmatch("/".join(parts[:n])) for n in range(1, len(parts) + 1))

    def owner_of(self, path):
        """Owners of the last matching rule (org prefix dropped), comma-joined; None if unowned."""
        owner = None
        for _, regex, owners in self.rules:
            if self._matches(regex, path):
                owner = ", ".join(_short(o) for o in owners)
        return owner

    def in_scope(self, path, team=TEAM):
        """True when any pattern naming `team` matches `path`."""
        return any(team in owners and self._matches(regex, path)
                   for _, regex, owners in self.rules)
