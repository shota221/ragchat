from dataclasses import dataclass


@dataclass
class ConfirmSearchEngineSyncJobResult:
    status: str # IN_PROGRESS, COMPLETED
    end_time: str = None
    