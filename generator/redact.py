"""API-key obfuscation applied to fetched files and to the generated output (M5)."""
import re

KEY_RE = re.compile(r"key=[A-Za-z0-9_\-]{8,}")


def redact(text):
    """Replace every `key=<token>` (token of 8+ [A-Za-z0-9_-]) with `key=***`."""
    return KEY_RE.sub("key=***", text)
