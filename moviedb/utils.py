"""Utility functions."""

import secrets
import uuid
import boto3
from flask import current_app


def generate_secret_key():
    """Generate a random string of 50 characters."""
    chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    secret_len = 50
    return "".join(secrets.choice(chars) for i in range(secret_len))


def is_valid_uuid_v4(id_str):
    try:
        uuid_obj = uuid.UUID(id_str, version=4)
        return str(uuid_obj) == id_str
    except ValueError:
        return False


def kebab_case(text: str) -> str:
    """Convert text to kebab case"""
    return text.lower().replace(" ", "-")


def upload_to_s3(file_obj, object_key, content_type=None):
    """Upload a file-like object to an S3 bucket.

    Args:
        file_obj: A file-like object (e.g. from ``request.files["poster"]``).
        bucket_name: The S3 bucket name.
        object_key: The S3 object key / path (e.g. ``"posters/filename.jpg"``).
        content_type: Optional MIME type to set on the object.
    """
    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    s3 = boto3.client("s3")
    s3.upload_fileobj(
        file_obj, current_app.config["S3_BUCKET_NAME"], object_key, ExtraArgs=extra_args
    )
