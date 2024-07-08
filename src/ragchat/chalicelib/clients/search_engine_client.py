import os
from dataclasses import asdict, dataclass
from typing import List
import boto3
from injector import singleton
from chalicelib.dataclasses.information_fragment import InformationFragment


@dataclass
class DataSourceSyncJobListCondition:
    status: str = None
    # max_resultsだけ取得して、そこからstatusでgrepするっぽい
    max_results: int = 5


@dataclass
class SearchCondition:
    query_text: str
    source_uris: List[str] = None
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

    def search(self, condition: SearchCondition):
        or_all_filters = []
        if condition.source_uris:
            or_all_filters.append({
                "ContainsAny": {
                    "Key": "source_uris",
                    "Value": {"StringListValue": condition.source_uris},
                }
            })

        if condition.category_ids:
            or_all_filters.append({
                "ContainsAny": {
                    "Key": "category_ids",
                    "Value": {"StringListValue": condition.category_ids},
                }
            })

        attribute_filter = {
            "AndAllFilters": [
                {
                    "EqualsTo": {
                        "Key": "_language_code",
                        "Value": {"StringValue": "ja"},
                    },
                },
                { 
                    "OrAllFilters": or_all_filters
                }
            ]
        }

        response = self.client.retrieve(
            QueryText=condition.query_text,
            IndexId=self.index_id,
            AttributeFilter=attribute_filter,
            PageSize=condition.page_size,
        )

        print(response)

        return [
            InformationFragment(
                text=highlight.get("Content","").replace('\\n', ' '),
                source=highlight.get("DocumentTitle","")
            )
            for highlight in response.get("ResultItems", [])
        ]