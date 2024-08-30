from dataclasses import dataclass
from typing import List

@dataclass
class DocCheckQueueMessageBody:
    check_type: str # "CHECKLIST" or "CONSISTENCY" or "TYPO"
    payload: object