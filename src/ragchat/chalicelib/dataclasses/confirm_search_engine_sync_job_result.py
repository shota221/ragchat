from dataclasses import dataclass


@dataclass
class ConfirmSearchEngineSyncJobResult:
    status: str # PENDING, IN_PROGRESS, COMPLETED
    end_time: str = None
    