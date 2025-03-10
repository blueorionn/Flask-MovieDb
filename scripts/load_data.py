"""Standalone script to load data to mongodb."""

import os
import sys
import argparse
import json
import pymongo


def main():
    # Add arguments
    parser = argparse.ArgumentParser(
        prog="Upload data",
        description=("Load json data to mongodb."),
        epilog="Bye! :)",
    )
    parser.add_argument("file_path", help="Path of json file.")
    args = parser.parse_args()

    # given file path
    file_path: str = args.file_path

    # checking if file exists.
    if not os.path.isfile(os.path.join(os.getcwd(), file_path)):
        sys.stdout.write("Given file doesn't exist. \n")
        sys.exit(1)

    if os.path.splitext(file_path)[-1] != ".json":
        sys.stdout.write("Given file is not a valid json file. \n")
        sys.exit(1)

    # reading file
    json_data = []
    with open(file_path, "r") as f:
        json_data = json.load(f)

    # creating mongoclient
    client = pymongo.MongoClient(os.environ.get("MONGO_URI"))  # Use your MongoDB URI

    # movies database
    sys.stdout.write("Creating or Accessing movies database \n")
    db = client["movies"]

    # movie collection
    sys.stdout.write("Creating or Accessing movie collection \n")
    collection = db["movie"]

    if isinstance(json_data, list):
        sys.stdout.write("Inserting list of documents. \n")
        collection.insert_many(json_data)
    else:
        sys.stdout.write("Inserting single document. \n")
        collection.insert_one(json_data)


if __name__ == "__main__":
    main()
