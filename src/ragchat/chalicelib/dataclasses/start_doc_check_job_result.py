from dataclasses import dataclass
from chalicelib.dataclasses.check_document_result import CheckDocumentResult

@dataclass
class StartDocCheckJobResult:
    job_id: str