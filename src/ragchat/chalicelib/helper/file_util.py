import os
import json
import urllib.parse

S3_SOURCE_BUCKET_NAME = os.environ["S3_SOURCE_BUCKET_NAME"]
META_FILE_PREFIX = "meta/"
META_FILE_SUFFIX = ".metadata.json"
INHIBITOR_FILE_PREFIX = "inhibitor/"
PREPROCESSING_FLAG_SUFFIX = ".preprocessing.flag"
HTTP_FILE_URI_PREFIX = (
    "https://s3-"
    + os.environ["AWS_DEFAULT_REGION"]
    + ".amazonaws.com/"
    + S3_SOURCE_BUCKET_NAME
    + "/"
)
HTTP_FILE_URI_PREFIX_2 = (
    "https://"
    + S3_SOURCE_BUCKET_NAME
    + ".s3."
    + os.environ["AWS_DEFAULT_REGION"]
    + ".amazonaws.com/"
)
S3_FILE_URI_PREFIX = "s3://" + S3_SOURCE_BUCKET_NAME + "/"
TMP_META_FILENAME = "tmp.metadata.json"
SYNC_PENDING_FLAG = "sync_pending.flag"


def is_meta_file(key):
    return key.startswith(META_FILE_PREFIX) and key.endswith(META_FILE_SUFFIX)


def is_meta_object(key):
    return key.startswith(META_FILE_PREFIX)


def is_inhibitor_object(key):
    return key.startswith(INHIBITOR_FILE_PREFIX)


def guess_meta_dir(source_key):
    return f"{META_FILE_PREFIX}{guess_preprocessing_destination_dir(source_key)}"


def guess_meta_key_by_destination_key(destination_key):
    return f"{META_FILE_PREFIX}{destination_key}{META_FILE_SUFFIX}"


def guess_tmp_meta_key(source_key):
    return f"{guess_meta_dir(source_key)}{TMP_META_FILENAME}"


def generate_meta(source_key, attributes=None):
    http_file_uri = HTTP_FILE_URI_PREFIX + source_key
    http_encoded_file_uri = HTTP_FILE_URI_PREFIX + urllib.parse.quote(source_key)
    http_file_uri_2 = HTTP_FILE_URI_PREFIX_2 + source_key
    http_encoded_file_uri_2 = HTTP_FILE_URI_PREFIX_2 + urllib.parse.quote(source_key)
    s3_file_uri = S3_FILE_URI_PREFIX + source_key
    s3_encoded_file_uri = S3_FILE_URI_PREFIX + urllib.parse.quote(source_key)
    meta = {
        "Attributes": {
            "alias": [source_key],
            "source_uris": [
                http_file_uri,
                http_encoded_file_uri,
                http_file_uri_2,
                http_encoded_file_uri_2,
                s3_file_uri,
                s3_encoded_file_uri,
            ],
        },
    }

    if attributes:
        meta = overwrite_meta(meta, attributes)
    return meta


def overwrite_meta(meta, attributes):
    for key, value in attributes.items():
        if isinstance(value, list):
            attributes[key] = [str(v) for v in value]
        meta["Attributes"][key] = attributes[key]
    return meta


def guess_preprocessing_destination_dir(source_key):
    splited_key = os.path.splitext(source_key)
    return f"{splited_key[1].replace('.', '')}/{splited_key[0]}/"


def guess_preprocessing_flag_key(source_key):
    return f"{INHIBITOR_FILE_PREFIX}{source_key}{PREPROCESSING_FLAG_SUFFIX}"
