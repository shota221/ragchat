from dataclasses import dataclass
from typing import List
from chalicelib.dataclasses.check_document_result import CheckDocumentResult

@dataclass
class ConsistencyResultItem:
    quote: str
    comment: str


@dataclass
class CheckDocumentConsistencyResult(CheckDocumentResult):
    result: List[ConsistencyResultItem]
