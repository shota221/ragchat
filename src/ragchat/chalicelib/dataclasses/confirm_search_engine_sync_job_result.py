from dataclasses import dataclass


@dataclass
class ConfirmSearchEngineSyncJobResult:
    status: str # IN_PROGRESS, COMPLETED
    