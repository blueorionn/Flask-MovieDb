"""User registration script"""

import os
import uuid
import argparse
import bcrypt
import sys
import datetime
import pymongo


def main():
    MONGO_URI = os.environ.get("MONGO_URI")

    if MONGO_URI == None or len(MONGO_URI) < 1:
        raise ValueError("Invalid or emtpy mongodb uri")

    # Add arguments
    parser = argparse.ArgumentParser(
        prog="Register Users",
        description=("Register users by creating data row in users table."),
        epilog="User Created! :)",
    )
    parser.add_argument("-fn", "--first-name", help="Firstname of the user.")
    parser.add_argument("-ln", "--last-name", help="Lastname of the user.")
    parser.add_argument("-u", "--username", help="Username of the user.")
    parser.add_argument(
        "-p", "--password", help="Password of the user. Minimum 8 char long."
    )
    args = parser.parse_args()

    # Get Arguments
    id = str(uuid.uuid4())
    first_name: str = args.first_name
    last_name: str = args.last_name
    user_name: str = args.username
    password: str = args.password
    created_at = datetime.datetime.now()

    # Check argument validity
    if first_name == None or len(first_name) < 1:
        raise ValueError("Invalid or empty Firstname. Arguments -fn or --first-name")
    if user_name == None or len(user_name) < 1:
        raise ValueError("Invalid or empty Username. Arguments -u or --username")
    if last_name == None or len(last_name) < 1:
        # lastname is not required
        last_name = None
    if password == None or len(password) < 8:
        raise ValueError(
            "Invalid or empty Password. Arguments -p or --password. Required minimum 8 chars."
        )
    else:
        password_encoded = password.encode("utf-8")
        salt = bcrypt.gensalt()
        password = bcrypt.hashpw(password_encoded, salt)

    # creating mongoclient
    client = pymongo.MongoClient(os.environ.get("MONGO_URI"))

    # auth database
    sys.stdout.write("Creating or Accessing auth database \n")
    db = client["auth"]

    # user collection
    sys.stdout.write("Creating or Accessing user collection \n")
    user_collection = db["user"]

    # Inserting data
    data = {
        "id": id,
        "firstname": first_name,
        "last_name": last_name,
        "username": user_name,
        "password": password.decode("utf-8"),
        "created_at": created_at,
    }
    user_collection.insert_one(data)

    sys.stdout.write("User created successfully. \n")


if __name__ == "__main__":
    main()
