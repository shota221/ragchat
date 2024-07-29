from dataclasses import dataclass



@dataclass
class CheckDocumentResult:
    checklist : list # list of ChecklistItem
    typos : list # list of TyposItem
    summary : str

@dataclass
class ChecklistItem:
    id: str
    result: bool
    quotes: list
    references: list
    comment: str

@dataclass
class TyposItem:
    original: str
    corrected: str
