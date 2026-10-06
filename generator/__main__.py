"""CLI: python3 -m generator --out out [--extra-catalog name=path …]

Fetches go-sdk-android and the consumer repos read-only, then writes
<out>/data.json, <out>/dashboard.html and the fetched state.csv files under <out>/raw/.
"""
import argparse
import json
import os
import sys

from generator import build, html
from generator.redact import redact


def _extra(value):
    name, sep, path = value.partition("=")
    if not (sep and name and path):
        raise argparse.ArgumentTypeError("expected name=path")
    return name, path


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m generator")
    parser.add_argument("--out", default="out", help="output directory (default: out)")
    parser.add_argument("--extra-catalog", type=_extra, action="append", default=[],
                        metavar="NAME=PATH",
                        help="extra version catalog shown in its own section, never as a consumer")
    args = parser.parse_args(argv)

    kwargs, raw_states = build.collect(dict(args.extra_catalog))
    model = build.assemble(**kwargs)

    os.makedirs(args.out, exist_ok=True)
    for module, text in raw_states.items():
        path = os.path.join(args.out, "raw", module, build.STATE_FILE)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    with open(os.path.join(args.out, "data.json"), "w", encoding="utf-8") as fh:
        fh.write(redact(json.dumps(model, indent=2, sort_keys=True)) + "\n")
    with open(os.path.join(args.out, "dashboard.html"), "w", encoding="utf-8") as fh:
        fh.write(html.render(model))
    print(f"wrote {args.out}/data.json, {args.out}/dashboard.html, "
          f"{len(raw_states)} state.csv files under {args.out}/raw/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
