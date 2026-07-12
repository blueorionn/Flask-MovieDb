"""Standalone script to load JSON seed data into MongoDB.

Usage:
    python scripts/load_data.py data/movies.json
    python scripts/load_data.py data/user.json --drop
    python scripts/load_data.py data/movies.json --collection movie
"""

import os
import sys
import argparse
import json
import datetime

import pymongo
from pymongo.uri_parser import parse_uri


def _extract_db_name(uri: str) -> str | None:
    """Extract the database name from a MongoDB URI string."""
    parsed = parse_uri(uri)
    return parsed.get("database")


def _convert_extended_json(obj):
    """Recursively convert MongoDB Extended JSON to native Python types.

    Handles ``{"$date": {"$numberLong": "..."}}`` → :class:`datetime.datetime`.
    Other types are returned as-is.
    """
    if isinstance(obj, dict):
        # Match Extended JSON date format
        if (
            "$date" in obj
            and isinstance(obj["$date"], dict)
            and "$numberLong" in obj["$date"]
        ):
            timestamp_ms = int(obj["$date"]["$numberLong"])
            return datetime.datetime.fromtimestamp(
                timestamp_ms / 1000.0, tz=datetime.timezone.utc
            )

        return {k: _convert_extended_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_convert_extended_json(item) for item in obj]

    return obj


def _infer_collection(file_path: str) -> str:
    """Infer the MongoDB collection name from the JSON filename."""
    filename = os.path.basename(file_path).lower()
    return "auth" if filename == "user.json" else "movie"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="load_data",
        description="Load JSON seed data into MongoDB.",
        epilog=(
            "Examples:\n"
            "  python scripts/load_data.py data/movies.json\n"
            "  python scripts/load_data.py data/user.json --drop\n"
            "  python scripts/load_data.py data/movies.json --collection movie"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("file_path", help="Path to the JSON file to import")
    parser.add_argument(
        "--collection",
        help="MongoDB collection to insert into (default: inferred from filename)",
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all existing documents in the collection before inserting",
    )
    args = parser.parse_args()

    # ── Validate file ──────────────────────────────────────────────────────
    file_path = args.file_path
    if not os.path.isfile(file_path):
        sys.stderr.write(f"Error: File not found: {file_path}\n")
        sys.exit(1)

    if os.path.splitext(file_path)[-1].lower() != ".json":
        sys.stderr.write(f"Error: Not a .json file: {file_path}\n")
        sys.exit(1)

    # ── Read JSON ──────────────────────────────────────────────────────────
    with open(file_path, "r") as f:
        raw_data = json.load(f)

    data_list = raw_data if isinstance(raw_data, list) else [raw_data]
    data_list = [_convert_extended_json(doc) for doc in data_list]

    if not data_list:
        sys.stderr.write("Error: No data found in file.\n")
        sys.exit(1)

    # ── MongoDB connection ─────────────────────────────────────────────────
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

    collection_name = args.collection or _infer_collection(file_path)

    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # ── Optional drop ──────────────────────────────────────────────────────
    if args.drop:
        deleted = collection.delete_many({}).deleted_count
        sys.stdout.write(
            f"Dropped {deleted} existing document(s) from "
            f"`{db_name}` → `{collection_name}`.\n"
        )

    # ── Insert ─────────────────────────────────────────────────────────────
    result = collection.insert_many(data_list)
    sys.stdout.write(
        f"Inserted {len(result.inserted_ids)} document(s) into "
        f"`{db_name}` → `{collection_name}`.\n"
    )


if __name__ == "__main__":
    main()
