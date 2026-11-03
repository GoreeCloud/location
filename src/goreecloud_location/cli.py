"""Administration commands: local-only account setup and development server."""
from __future__ import annotations

import argparse
from pathlib import Path
from getpass import getpass
import sqlite3

from .store import backup_database, create_account, default_db_path, initialize


def main():
    parser = argparse.ArgumentParser(prog="gclocation", description="GoreeCloud Location admin CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    admin = sub.add_parser("create-admin", help="Create a local user without opening public signup")
    admin.add_argument("--username", required=True)
    backup = sub.add_parser("backup", help="Save a consistent private SQLite database snapshot")
    backup.add_argument("--destination", required=True, help="New file; existing backups are never overwritten")
    serve = sub.add_parser("serve", help="Run a loopback-bound development service")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8123)
    serve.add_argument("--i-understand-network-exposure", action="store_true")
    args = parser.parse_args()

    if args.command == "create-admin":
        path = default_db_path()
        initialize(path)
        first = getpass("New password (14+ characters): ")
        second = getpass("Confirm password: ")
        if first != second:
            parser.error("Passwords do not match.")
        try:
            create_account(path, args.username, first)
        except (ValueError, sqlite3.IntegrityError) as exc:
            parser.error(str(exc))
        print(f"Created account '{args.username}'. Location data stays in {path}.")
    elif args.command == "backup":
        source = default_db_path()
        try:
            backup_database(source, Path(args.destination).expanduser())
        except (OSError, ValueError, sqlite3.Error) as exc:
            parser.error(str(exc))
        print(f"Backup created: {args.destination}. Protect this copy as sensitive location data.")
    elif args.command == "serve":
        if args.host not in ("127.0.0.1", "::1", "localhost") and not args.i_understand_network_exposure:
            parser.error("Non-loopback access requires --i-understand-network-exposure and a TLS/auth reverse proxy.")
        import uvicorn
        uvicorn.run("goreecloud_location.main:app", host=args.host, port=args.port, workers=1)


if __name__ == "__main__":
    main()
