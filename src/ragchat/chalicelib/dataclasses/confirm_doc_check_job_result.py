from dataclasses import dataclass
from chalicelib.dataclasses.check_document_result import CheckDocumentResult
@dataclass
class ConfirmDocCheckJobResult:
    status: str # PENDING, IN_PROGRESS, COMPLETED, FAILED
    payload: CheckDocumentResult = None
    