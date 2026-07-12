"""Standalone diagnostic script for the testing environment.

Usage:
    python run_test.py
"""

import os
import sys
import pytest
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    # Override to testing environment
    os.environ["FLASK_ENV"] = "testing"
    print(f"FLASK_ENV  = {os.environ['FLASK_ENV']}")

    # Testing database connection
    mongo_uri = "mongodb://localhost:27017/testdb"
    print(f"MONGO_URI  = {mongo_uri}")

    import pymongo

    try:
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # The admin command "ping" is the standard MongoDB health check
        client.admin.command("ping")
        print()
        print("✓ Database is reachable and responding.")
        client.close()
    except Exception as exc:
        print()
        sys.stderr.write(f"✗ Database is NOT reachable: {exc}\n")
        sys.exit(1)

    # Run tests
    pytest.main(["cinexa/", "-v"])


if __name__ == "__main__":
    main()
