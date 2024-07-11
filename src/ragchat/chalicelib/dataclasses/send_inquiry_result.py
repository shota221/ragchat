from dataclasses import dataclass


@dataclass
class SendInquiryResult:
    assistant_text: str
    vectors: dict