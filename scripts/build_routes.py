#!/usr/bin/env python3
"""
Build an AmneziaVPN routing JSON from a template and TXT input files.

Supported input:
- IPv4 addresses: 1.2.3.4
- IPv4 CIDR:      1.2.3.0/24
- Domains:        example.com

Each non-empty, non-comment line becomes one JSON entry:
{
    "hostname": "<value>",
    "ip": "",
    "ips": []
}

The original template entries are preserved.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path


def read_values(input_dir: Path) -> list[str]:
    values: set[str] = set()

    for path in sorted(input_dir.glob("*.txt")):
        for lineno, raw in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(), start=1
        ):
            value = raw.split("#", 1)[0].strip()
            if not value:
                continue

            # Validate IP/CIDR; otherwise treat as a domain/hostname.
            try:
                ipaddress.ip_network(value, strict=False)
            except ValueError:
                if not is_valid_domain(value):
                    raise ValueError(
                        f"{path}:{lineno}: invalid IP/CIDR or domain: {value!r}"
                    )

            values.add(value)

    return sorted(values, key=sort_key)


def is_valid_domain(value: str) -> bool:
    # Intentionally conservative; supports normal DNS names and wildcards.
    if len(value) > 253 or " " in value or "/" in value:
        return False
    value = value.removeprefix("*.")
    if not value or "." not in value:
        return False

    labels = value.rstrip(".").split(".")
    for label in labels:
        if not label or len(label) > 63:
            return False
        if label[0] == "-" or label[-1] == "-":
            return False
        if not all(c.isalnum() or c == "-" for c in label):
            return False
    return True


def sort_key(value: str):
    try:
        net = ipaddress.ip_network(value, strict=False)
        return (0, int(net.network_address), net.prefixlen, value)
    except ValueError:
        return (1, value.lower())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    template = json.loads(args.template.read_text(encoding="utf-8"))
    if not isinstance(template, list):
        raise ValueError("Template root must be a JSON array.")

    for i, item in enumerate(template):
        if not isinstance(item, dict):
            raise ValueError(f"Template entry {i} must be an object.")
        for key in ("hostname", "ip", "ips"):
            if key not in item:
                raise ValueError(f"Template entry {i} is missing key {key!r}.")

    existing = {item["hostname"] for item in template}
    generated = []

    for value in read_values(args.input_dir):
        if value in existing:
            continue
        generated.append({"hostname": value, "ip": "", "ips": []})
        existing.add(value)

    result = template + generated
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )

    print(f"Template entries preserved: {len(template)}")
    print(f"New entries added:          {len(generated)}")
    print(f"Total JSON entries:         {len(result)}")
    print(f"Output:                     {args.output}")


if __name__ == "__main__":
    main()
