from dataclasses import dataclass
from typing import List
from chalicelib.dataclasses.check_document_result import CheckDocumentResult

@dataclass
class TypoResultItem:
    original: str
    corrected: str


@dataclass
class CheckDocumentTypoResult(CheckDocumentResult):
    result: List[TypoResultItem]
