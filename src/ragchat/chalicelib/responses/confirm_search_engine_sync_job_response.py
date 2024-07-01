from dataclasses import dataclass


@dataclass
class ConfirmSearchEngineSyncJobResponse:
    status: str # IN_PROGRESS, COMPLETED
    