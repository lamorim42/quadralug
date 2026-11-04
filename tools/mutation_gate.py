#!/usr/bin/env python3
"""Compara o relatório do mutmut com a meta de mutação. Só biblioteca padrão."""

import argparse
import json
import sys
from pathlib import Path

THRESHOLD = 80


def gate_passes(killed: int, total: int) -> bool:
    return total > 0 and killed * 100 >= total * THRESHOLD


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)

    if not args.report.is_file():
        print(f"relatório de mutação ausente: {args.report}", file=sys.stderr)
        return 1

    stats = json.loads(args.report.read_text(encoding="utf-8"))
    killed, total = int(stats["killed"]), int(stats["total"])
    if gate_passes(killed, total):
        print(f"mutação: {killed} de {total} mortos, meta {THRESHOLD}%")
        return 0

    print(f"mutação abaixo da meta: {killed} de {total}, meta {THRESHOLD}%", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
