import json
import os
from dataclasses import asdict
import boto3
from chalicelib.dataclasses.confirm_search_engine_sync_job_result import (
    ConfirmSearchEngineSyncJobResult,
)
from chalicelib.enums.confirm_search_engine_sync_job_status import (
    ConfirmSearchEngineSyncJobStatus,
)


class SearchEngineService:
    def __init__(self):
        self.client = boto3.client("kendra")
        self.index_id = os.environ.get("KENDRA_INDEX_ID")
        self.data_source_id = os.environ.get("KENDRA_DATA_SOURCE_ID")

    def request_sync_job(self):
        response = self.client.start_data_source_sync_job(
            Id=self.data_source_id, IndexId=self.index_id
        )

        return response

    def confirm_sync_job(self):
        if self.__is_syncing():
            return asdict(
                ConfirmSearchEngineSyncJobResult(
                    status=ConfirmSearchEngineSyncJobStatus.IN_PROGRESS.value
                )
            )

        if self.__is_completed_nomally():
            return asdict(
                ConfirmSearchEngineSyncJobResult(
                    status=ConfirmSearchEngineSyncJobStatus.COMPLETED.value
                )
            )

        self.request_sync_job()

        return asdict(
            ConfirmSearchEngineSyncJobResult(
                status=ConfirmSearchEngineSyncJobStatus.IN_PROGRESS.value
            )
        )

    def __is_syncing(self):
        syncing_list = self.client.list_data_source_sync_jobs(
            Id=self.data_source_id, IndexId=self.index_id, StatusFilter="SYNCING"
        )

        if syncing_list.get("History", []):
            return True

        indexing_list = self.client.list_data_source_sync_jobs(
            Id=self.data_source_id,
            IndexId=self.index_id,
            StatusFilter="SYNCING_INDEXING",
        )

        if indexing_list.get("History", []):
            return True

        return False

    def __is_completed_nomally(self):
        latest_success_list = self.client.list_data_source_sync_jobs(
            Id=self.data_source_id,
            IndexId=self.index_id,
            MaxResults=2,
            StatusFilter="SUCCEEDED",
        )

        if len(latest_success_list.get("History", [])) < 2:
            print("Latest success list is less than 2")
            return False

        latest_job_summary = latest_success_list.get("History", [])[0]

        latest_scanned_count = int(
            latest_job_summary.get("Metrics", {}).get("DocumentsScanned")
        )

        latest_added_count = int(
            latest_job_summary.get("Metrics", {}).get("DocumentsAdded")
        )

        latest_deleted_count = int(
            latest_job_summary.get("Metrics", {}).get("DocumentsDeleted")
        )

        if latest_deleted_count == 0:
            return True

        second_latest_success_job_summary = latest_success_list.get("History", [])[1]

        second_latest_scanned_count = int(
            second_latest_success_job_summary.get("Metrics", {}).get("DocumentsScanned")
        )

        expected_latest_scanned_count = (
            second_latest_scanned_count + latest_added_count - latest_deleted_count
        )

        if latest_scanned_count != expected_latest_scanned_count:
            print("Scanned count is not expected")
            return False

        return True
