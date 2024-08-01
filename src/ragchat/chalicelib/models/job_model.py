import os
from dataclasses import dataclass
from chalicelib.models.base_model import BaseModel
from chalicelib.dataclasses.check_document_result import CheckDocumentResult

@dataclass
class JobModel(BaseModel):
    job_id: str
    status: str # PENDING, IN_PROGRESS, COMPLETED, FAILED
    payload: str = None

    @classmethod
    def table_name(cls):
        return os.environ.get('DYNAMODB_JOB_TABLE_NAME')
    
    @classmethod
    def primary_key_name(cls):
        return 'job_id'