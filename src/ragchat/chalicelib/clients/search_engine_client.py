import os
from dataclasses import asdict, dataclass
from typing import List
import boto3
from injector import singleton
from chalicelib.dataclasses.information_fragment import InformationFragment
from chalicelib.helper import file_util


@dataclass
class DataSourceSyncJobListCondition:
    status: str = None
    # max_resultsだけ取得して、そこからstatusでgrepするっぽい
    max_results: int = 5


@dataclass
class SearchCondition:
    query_text: str
    file_keys: List[str] = None
    category_ids: List[str] = None
    page_size: int = 10


@singleton
class SearchEngineClient:
    def __init__(self):
        self.client = boto3.client("kendra")
        self.index_id = os.environ.get("KENDRA_INDEX_ID")
        self.data_source_id = os.environ.get("KENDRA_DATA_SOURCE_ID")

    def start_data_source_sync_job(self):
        response = self.client.start_data_source_sync_job(
            Id=self.data_source_id, IndexId=self.index_id
        )

        return response

    def list_data_source_sync_jobs(self, condition: DataSourceSyncJobListCondition):
        response = self.client.list_data_source_sync_jobs(
            Id=self.data_source_id,
            IndexId=self.index_id,
            StatusFilter=condition.status,
            MaxResults=condition.max_results,
        )

        return response.get("History", [])

    def search(self, user_group_id, condition: SearchCondition):
        group_filter = {
            "ContainsAny": {
                "Key": "group_ids",
                "Value": {
                    "StringListValue": [
                        str(user_group_id),
                        file_util.ALL_GROUP_ID,
                    ]
                },
            }
        }

        or_all_filters = []

        if condition.file_keys:
            or_all_filters.append(
                {
                    "ContainsAny": {
                        "Key": "source_key",
                        "Value": {"StringListValue": condition.file_keys},
                    }
                }
            )

        if condition.category_ids:
            or_all_filters.append(
                {
                    "ContainsAny": {
                        "Key": "category_ids",
                        "Value": {"StringListValue": condition.category_ids},
                    }
                }
            )

        attribute_filter = {
            "AndAllFilters": [
                {
                    "EqualsTo": {
                        "Key": "_language_code",
                        "Value": {"StringValue": "ja"},
                    },
                },
                {"OrAllFilters": or_all_filters},
                group_filter,
            ]
        }

        response = self.client.retrieve(
            QueryText=condition.query_text,
            IndexId=self.index_id,
            AttributeFilter=attribute_filter,
            PageSize=condition.page_size,
            RequestedDocumentAttributes=["source_key", "source_name"],
        )

        print(response)

        information_fragments = []

        for highlight in response.get("ResultItems", []):
            text = highlight.get("Content", "").replace("\\n", " ")
            attrs = highlight.get("DocumentAttributes", [])
            source = next(
                (
                    attr["Value"]["StringListValue"][0]
                    for attr in attrs
                    if attr["Key"] == "source_name"
                ),
                "",
            )
            information_fragments.append(InformationFragment(text=text, source=source))

        return information_fragments
