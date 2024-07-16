from dataclasses import dataclass

@dataclass
class GeneralResult:
    result: str # SUCCESS, FAILURE
    message: str = ""