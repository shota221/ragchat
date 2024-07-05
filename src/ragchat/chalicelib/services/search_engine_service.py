import os
from datetime import datetime
import boto3
from injector import inject, Injector
from chalicelib.helper import result_handler, utc2jst
from chalicelib.dataclasses.confirm_search_engine_sync_job_result import (
    ConfirmSearchEngineSyncJobResult,
)
from chalicelib.enums.confirm_search_engine_sync_job_status import (
    ConfirmSearchEngineSyncJobStatus,
)
from chalicelib.clients.search_engine_client import (
    SearchEngineClient,
    DataSourceSyncJobListCondition,
)


class SearchEngineService:
    @inject
    def __init__(self, search_engine_client: SearchEngineClient):
        self.search_engine_client = search_engine_client

    @result_handler
    def request_sync_job(self):
        result = self.search_engine_client.start_data_source_sync_job()
        return result

    @result_handler
    def confirm_sync_job(self):
        if self.__is_syncing():
            return ConfirmSearchEngineSyncJobResult(
                    status=ConfirmSearchEngineSyncJobStatus.IN_PROGRESS.value
                )

        end_time = self.__get_nomally_completed_time()
        if end_time:
            utc_time=end_time.strftime('%Y-%m-%d %H:%M:%S')
            jst_time=utc2jst(utc_time)
            return ConfirmSearchEngineSyncJobResult(
                    status=ConfirmSearchEngineSyncJobStatus.COMPLETED.value,
                    end_time=jst_time
                )

        self.request_sync_job()

        return ConfirmSearchEngineSyncJobResult(
                status=ConfirmSearchEngineSyncJobStatus.IN_PROGRESS.value
            )

    def __is_syncing(self):
        syncing_list = self.search_engine_client.list_data_source_sync_jobs(
            DataSourceSyncJobListCondition(status="SYNCING")
        )

        if syncing_list:
            return True

        indexing_list = self.search_engine_client.list_data_source_sync_jobs(
            DataSourceSyncJobListCondition(status="SYNCING_INDEXING")
        )

        if indexing_list:
            return True

        return False

    def __get_nomally_completed_time(self):
        latest_success_list = self.search_engine_client.list_data_source_sync_jobs(
            DataSourceSyncJobListCondition(status="SUCCEEDED", max_results=2)
        )

        if len(latest_success_list) < 2:
            print("Latest success list is less than 2")
            return None

        latest_job_summary = latest_success_list[0]

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
            return latest_job_summary.get("EndTime")

        second_latest_success_job_summary = latest_success_list[1]

        second_latest_scanned_count = int(
            second_latest_success_job_summary.get("Metrics", {}).get("DocumentsScanned")
        )

        expected_latest_scanned_count = (
            second_latest_scanned_count + latest_added_count - latest_deleted_count
        )

        if latest_scanned_count != expected_latest_scanned_count:
            print("Scanned count is not expected")
            return None

        return latest_job_summary.get("EndTime")
