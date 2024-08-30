from dataclasses import dataclass
from typing import List
from chalicelib.dataclasses.check_document_result import CheckDocumentResult


@dataclass
class ChecklistResultItem:
    id: str
    quote: str
    comment: str


@dataclass
class CheckDocumentChecklistResult(CheckDocumentResult):
    result: List[ChecklistResultItem]
