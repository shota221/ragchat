from injector import singleton
from chalicelib.models.job_model import JobModel

@singleton
class JobRepository:
    @staticmethod
    def find_by_job_id(job_id):
        return JobModel.find({"job_id": {"S": job_id}})