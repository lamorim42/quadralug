#!/usr/bin/env python3
"""Regras de promoção de branches usadas pelos workflows. Só biblioteca padrão."""

import argparse
import re
import subprocess
import sys

VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")


def _is_branch_of(name: str, prefix: str) -> bool:
    return name.startswith(prefix) and len(name) > len(prefix)


def pr_route_allowed(head: str, base: str, same_repo: bool) -> bool:
    if not same_repo:
        return False
    if base == "develop":
        return head == "main" or _is_branch_of(head, "feature/")
    if base == "main":
        return head.startswith("release/") and valid_version(head.removeprefix("release/"))
    if _is_branch_of(base, "release/"):
        return _is_branch_of(head, "feature/")
    return False


def valid_version(version: str) -> bool:
    return VERSION_PATTERN.fullmatch(version) is not None


def release_exists(remote: str, version: str) -> bool:
    refs = (f"refs/heads/release/{version}", f"refs/tags/v{version}")
    output = subprocess.run(
        ["git", "ls-remote", remote, *refs], capture_output=True, text=True, check=True
    ).stdout
    return bool(output.strip())


def tag_for_merge(head: str, merged: bool, same_repo: bool) -> str | None:
    if not merged or not same_repo or not _is_branch_of(head, "release/"):
        return None
    version = head.removeprefix("release/")
    return f"v{version}" if valid_version(version) else None


def needs_backmerge(repo: str, develop_ref: str, release_ref: str) -> bool:
    output = subprocess.run(
        ["git", "-C", repo, "rev-list", "--count", f"{develop_ref}..{release_ref}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return int(output.strip()) > 0


def _check_pr(args: argparse.Namespace) -> int:
    same_repo = args.head_repo == args.base_repo
    if pr_route_allowed(args.head, args.base, same_repo):
        return 0
    print(f"rota de PR recusada: {args.head_repo}:{args.head} -> {args.base}", file=sys.stderr)
    return 1


def _check_release(args: argparse.Namespace) -> int:
    if not valid_version(args.version):
        print(f"versão inválida: {args.version}", file=sys.stderr)
        return 1
    if release_exists(args.remote, args.version):
        print(f"a branch ou a tag da versão {args.version} já existe", file=sys.stderr)
        return 1
    return 0


def _tag_for_merge(args: argparse.Namespace) -> int:
    tag = tag_for_merge(args.head, args.merged == "true", args.head_repo == args.base_repo)
    if tag is None:
        print(f"nenhuma tag para {args.head_repo}:{args.head}", file=sys.stderr)
        return 1
    print(f"tag={tag}")
    return 0


def _needs_backmerge(args: argparse.Namespace) -> int:
    needed = needs_backmerge(args.repo, args.develop, args.release)
    print(f"needed={str(needed).lower()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)

    check_pr = commands.add_parser("check-pr")
    check_pr.add_argument("--head", required=True)
    check_pr.add_argument("--base", required=True)
    check_pr.add_argument("--head-repo", required=True)
    check_pr.add_argument("--base-repo", required=True)
    check_pr.set_defaults(handler=_check_pr)

    check_release = commands.add_parser("check-release")
    check_release.add_argument("--version", required=True)
    check_release.add_argument("--remote", default="origin")
    check_release.set_defaults(handler=_check_release)

    merge = commands.add_parser("tag-for-merge")
    merge.add_argument("--head", required=True)
    merge.add_argument("--merged", required=True)
    merge.add_argument("--head-repo", required=True)
    merge.add_argument("--base-repo", required=True)
    merge.set_defaults(handler=_tag_for_merge)

    backmerge = commands.add_parser("needs-backmerge")
    backmerge.add_argument("--repo", default=".")
    backmerge.add_argument("--develop", required=True)
    backmerge.add_argument("--release", required=True)
    backmerge.set_defaults(handler=_needs_backmerge)

    args = parser.parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    sys.exit(main())
