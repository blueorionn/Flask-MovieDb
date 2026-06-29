"""Standalone script to register a new user in the database.

Usage:
    python scripts/register_user.py -fn Bob -u bob -p secret1234
    python scripts/register_user.py -fn Alice -u alice -p secret5678 --role admin
"""

import os
import uuid
import argparse
import sys
import datetime

import bcrypt
import pymongo
from pymongo.uri_parser import parse_uri


def _extract_db_name(uri: str) -> str | None:
    """Extract the database name from a MongoDB URI string."""
    parsed = parse_uri(uri)
    return parsed.get("database")


def main() -> None:
    # ── Connection setup ───────────────────────────────────────────────────
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        sys.stderr.write("Error: MONGO_URI environment variable is not set.\n")
        sys.exit(1)

    db_name = _extract_db_name(mongo_uri)
    if not db_name:
        sys.stderr.write(
            "Error: MONGO_URI must include a database name in the path, "
            "e.g. mongodb://localhost:27017/mydb\n"
        )
        sys.exit(1)

    # ── Argparse ───────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(
        prog="register_user",
        description="Register a new user in the database.",
        epilog="User created! :)",
    )
    parser.add_argument(
        "-fn", "--first-name",
        required=True,
        help="First name of the user",
    )
    parser.add_argument(
        "-ln", "--last-name",
        default=None,
        help="Last name of the user (optional)",
    )
    parser.add_argument(
        "-u", "--username",
        required=True,
        help="Username (must be unique)",
    )
    parser.add_argument(
        "-p", "--password",
        required=True,
        help="Password (minimum 8 characters)",
    )
    parser.add_argument(
        "-r", "--role",
        default="user",
        choices=["user", "admin"],
        help="User role (default: user)",
    )
    args = parser.parse_args()

    # ── Validate inputs ────────────────────────────────────────────────────
    first_name = args.first_name.strip()
    if not first_name:
        sys.stderr.write("Error: First name cannot be empty.\n")
        sys.exit(1)

    user_name = args.username.strip()
    if not user_name:
        sys.stderr.write("Error: Username cannot be empty.\n")
        sys.exit(1)

    last_name = args.last_name.strip() if args.last_name else None

    password = args.password
    if len(password) < 8:
        sys.stderr.write(
            "Error: Password must be at least 8 characters long.\n"
        )
        sys.exit(1)

    role = args.role

    # ── Hash password ──────────────────────────────────────────────────────
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    # ── MongoDB ────────────────────────────────────────────────────────────
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    user_collection = db["auth"]

    # Check for duplicate username
    duplicate = user_collection.find_one({"username": user_name})
    if duplicate is not None:
        sys.stderr.write(f"Error: User '{user_name}' already exists.\n")
        sys.exit(1)

    # Insert user document
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "firstname": first_name,
        "lastname": last_name,
        "username": user_name,
        "password": hashed_password.decode("utf-8"),
        "role": role,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    }
    user_collection.insert_one(user_doc)

    sys.stdout.write(
        f"User '{user_name}' ({role}) created successfully with ID {user_id}\n"
    )


if __name__ == "__main__":
    main()
