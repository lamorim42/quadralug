#!/usr/bin/env python3
"""Compara o relatório do mutmut com a meta de mutação. Só biblioteca padrão."""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_THRESHOLD = 80


def gate_passes(killed: int, total: int, threshold: int = DEFAULT_THRESHOLD) -> bool:
    return total > 0 and killed * 100 >= total * threshold


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    args = parser.parse_args(argv)

    if not args.report.is_file():
        print(f"relatório de mutação ausente: {args.report}", file=sys.stderr)
        return 1

    stats = json.loads(args.report.read_text(encoding="utf-8"))
    killed, total = int(stats["killed"]), int(stats["total"])
    if gate_passes(killed, total, args.threshold):
        print(f"mutação: {killed} de {total} mortos, meta {args.threshold}%")
        return 0

    print(f"mutação abaixo da meta: {killed} de {total}, meta {args.threshold}%", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
