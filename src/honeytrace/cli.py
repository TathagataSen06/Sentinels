"""Command-line interface.

Subcommands:

* ``run`` — load a configuration and run the honeypot.
* ``validate`` — parse and validate a configuration, then exit.
* ``list-services`` — print the registered decoy service types.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .config import Config, ConfigError, load_config
from .logging_setup import configure_logging, get_app_logger
from .server import HoneytraceServer
from .services import available_types

_DEFAULT_CONFIG_PATHS = (
    "config/honeytrace.yml",
    "/etc/honeytrace/honeytrace.yml",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="honeytrace",
        description="Honeytrace — a high-signal honeypot framework.",
    )
    parser.add_argument(
        "--version", action="version", version=f"honeytrace {__version__}"
    )
    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run", help="run the honeypot")
    run_cmd.add_argument(
        "-c", "--config", help="path to the configuration file", default=None
    )

    validate_cmd = sub.add_parser("validate", help="validate a configuration file")
    validate_cmd.add_argument(
        "-c", "--config", help="path to the configuration file", default=None
    )

    sub.add_parser("list-services", help="list available service types")

    return parser


def resolve_config_path(explicit: str | None) -> Path:
    """Determine which configuration file to use."""
    if explicit:
        return Path(explicit)
    env = os.environ.get("HONEYTRACE_CONFIG")
    if env:
        return Path(env)
    for candidate in _DEFAULT_CONFIG_PATHS:
        path = Path(candidate)
        if path.is_file():
            return path
    return Path(_DEFAULT_CONFIG_PATHS[0])


def _load(explicit: str | None) -> Config:
    path = resolve_config_path(explicit)
    return load_config(path)


def _cmd_run(args: argparse.Namespace) -> int:
    try:
        config = _load(args.config)
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    configure_logging(config.logging)
    logger = get_app_logger()
    logger.info("loaded configuration for node %r", config.node_id)
    return HoneytraceServer(config).serve()


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        config = _load(args.config)
    except ConfigError as exc:
        print(f"invalid: {exc}", file=sys.stderr)
        return 2
    enabled = [s.name for s in config.services if s.enabled]
    print(f"valid: node {config.node_id!r}, {len(enabled)} enabled service(s)")
    if enabled:
        print("enabled services: " + ", ".join(enabled))
    return 0


def _cmd_list_services(_: argparse.Namespace) -> int:
    for name in available_types():
        print(name)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _cmd_run(args)
    if args.command == "validate":
        return _cmd_validate(args)
    if args.command == "list-services":
        return _cmd_list_services(args)

    parser.print_help(sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
