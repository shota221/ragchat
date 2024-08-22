import os
import json
import urllib.parse

S3_SOURCE_BUCKET_NAME = os.environ["S3_SOURCE_BUCKET_NAME"]
META_FILE_PREFIX = "meta/"
META_FILE_SUFFIX = ".metadata.json"
INHIBITOR_FILE_PREFIX = "inhibitor/"
PREPROCESSING_FLAG_SUFFIX = ".preprocessing.flag"
TMP_META_FILENAME = "tmp.metadata.json"
SYNC_PENDING_FLAG = "sync_pending.flag"
PDF_EXTENSION = ".pdf"
WORD_EXTENSION = ".docx"
ALL_GROUP_ID = "all"


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
    meta = {
        "Attributes": {
            "source_key": [source_key],
            "source_name": [os.path.basename(source_key)],
            "category_ids": [],
            "group_ids": [ALL_GROUP_ID]
        }
    }

    if attributes:
        meta = overwrite_meta(meta, attributes)
    return meta


def overwrite_meta(meta, attributes):
    for key, value in attributes.items():
        if key == "file_name":
            meta["Attributes"]["source_name"] = [value]
        elif key == "category_ids":
            meta["Attributes"][key] = [str(i) for i in value]
        elif key == "group_ids":
            meta["Attributes"][key] = [str(i) for i in value] or [ALL_GROUP_ID]
    return meta


def guess_preprocessing_destination_dir(source_key):
    splited_key = os.path.splitext(source_key)
    return f"{splited_key[1].replace('.', '')}/{splited_key[0]}/"


def guess_preprocessing_flag_key(source_key):
    return f"{INHIBITOR_FILE_PREFIX}{source_key}{PREPROCESSING_FLAG_SUFFIX}"


def is_pdf(key):
    return key.lower().endswith(PDF_EXTENSION)


def is_word(key):
    return key.lower().endswith(WORD_EXTENSION)
