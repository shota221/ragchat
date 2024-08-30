import os
import json
from dataclasses import asdict
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring
import docx
from io import BytesIO
import pypdfium2
import boto3
from injector import inject
from aws_lambda_powertools.utilities.validation import validate
from chalicelib.helper import result_handler, PromptBuilder, file_util
from chalicelib.clients.generation_ai_client import GenerationAiClient
from chalicelib.clients.queueing_client import QueueingClient
from chalicelib.clients.storage_client import StorageClient
from chalicelib.dataclasses.check_document_checklist_result import (
    ChecklistResultItem,
    CheckDocumentChecklistResult
)
from chalicelib.dataclasses.check_document_consistency_result import (
    ConsistencyResultItem,
    CheckDocumentConsistencyResult
)
from chalicelib.dataclasses.check_document_typo_result import (
    TypoResultItem,
    CheckDocumentTypoResult
)
from chalicelib.dataclasses.doc_check_queue_message_body import DocCheckQueueMessageBody
from chalicelib.dataclasses.start_doc_check_job_result import StartDocCheckJobResult
from chalicelib.dataclasses.confirm_doc_check_job_result import ConfirmDocCheckJobResult
from chalicelib.schemas import check_document_checklist_schema, check_document_typo_schema, check_document_consistency_schema
from chalicelib.models.job_model import JobModel
from chalicelib.repositories.job_repository import JobRepository
from chalicelib.enums.job_status import JobStatus
from chalicelib.enums.doc_check_type import DocCheckType
from chalicelib.schemas import generation_ai_schema


class DocumentService:
    S3_DOCUMENT_BUCKET_NAME = os.environ["S3_DOCUMENT_BUCKET_NAME"]
    SQS_DOC_CHECK_QUEUE_NAME = os.environ["SQS_DOC_CHECK_QUEUE_NAME"]
    PDF_EXTENSION = ".pdf"
    WORD_EXTENSION = ".docx"
    ASSISTANT_TEXT_PREFIX = "["
    ASSISTANT_TEXT_SUFFIX = "]"
    CHECKLIST_CHUNK_SIZE = 20
    CHECKLIST_SIZE_THRESHOLD = 10

    @inject
    def __init__(
        self,
        generation_ai_client: GenerationAiClient,
        queueing_client: QueueingClient,
        storage_client: StorageClient,
        job_repository: JobRepository,
    ):
        self.generation_ai_client = generation_ai_client
        self.queueing_client = queueing_client
        self.storage_client = storage_client
        self.job_repository = job_repository
        self.prompt_builder = PromptBuilder()
    
    @result_handler
    def check_typo(self, json_body):
        validate(event=json_body, schema=check_document_typo_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")

        document = self.__extract_text(target_key)

        prompt = self.prompt_builder.build_doc_typo_check_prompt(document)
        res = self.__assistant_check_result(prompt, generation_ai_schema.DOC_TYPO_CHECK)

        return CheckDocumentTypoResult(
            result=[
                TypoResultItem(
                    original=item["org"],
                    corrected=item["cor"],
                )
                for item in res if item["org"] != item["cor"]
            ],
        )
    
    @result_handler
    def check_consistency(self, json_body):
        validate(event=json_body, schema=check_document_consistency_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")
        
        reference_key = json_body["reference_key"]
        if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, reference_key):
            raise Exception(f"File not found: {reference_key}")
        
        document = self.__extract_text(target_key)
        reference = self.__extract_text(reference_key)

        prompt = self.prompt_builder.build_doc_consistency_check_prompt(document, reference)

        res = self.__assistant_check_result(prompt, generation_ai_schema.DOC_CONSISTENCY_CHECK)

        return CheckDocumentConsistencyResult(
            result=[
                ConsistencyResultItem(
                    quote=item["qot"],
                    comment=item["cmt"],
                )
                for item in res
            ],
        )

    @result_handler
    def check_checklist(self, json_body):
        validate(event=json_body, schema=check_document_checklist_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")
        
        document = self.__extract_text(target_key)
        checklist = json_body["checklist"]
        
        if json_body.get("reference_key"):
            reference_key = json_body["reference_key"]
            if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, reference_key):
                raise Exception(f"File not found: {reference_key}")
            reference = self.__extract_text(reference_key)
            prompt = self.prompt_builder.build_doc_checklist_check_with_reference_prompt(
                document, json.dumps(checklist, ensure_ascii=False), reference
            )
        else:
            prompt = self.prompt_builder.build_doc_checklist_check_prompt(
                document, json.dumps(checklist, ensure_ascii=False)
            )
        
        res = self.__assistant_check_result(prompt, generation_ai_schema.DOC_CHECKLIST_CHECK)

        return CheckDocumentChecklistResult(
            result=[
                ChecklistResultItem(
                    id=item["id"],
                    quote=item["qot"],
                    comment=item["cmt"],
                )
                for item in res
            ],
        )                

    def __assistant_check_result(self, prompt, result_schema):
        assistant_text = self.ASSISTANT_TEXT_PREFIX
        assistant_text = assistant_text + self.generation_ai_client.generate_message(
            prompt, assistant_text, max_tokens=8192, top_p=0.1
        )
        assistant_text = assistant_text[
            : assistant_text.rfind(self.ASSISTANT_TEXT_SUFFIX) + 1
        ]
        result = json.loads(assistant_text)
        validate(event=result, schema=result_schema)
        return result

    @result_handler
    def start_checklist_check_job(self, json_body):
        validate(event=json_body, schema=check_document_checklist_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")
        if json_body.get("reference_key"):
            reference_key = json_body["reference_key"]
            if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, reference_key):
                raise Exception(f"File not found: {reference_key}")
        return self.__start_check_job(json_body, DocCheckType.CHECKLIST)
    
    @result_handler
    def start_consistency_check_job(self, json_body):
        validate(event=json_body, schema=check_document_consistency_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")
        reference_key = json_body["reference_key"]
        if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, reference_key):
            raise Exception(f"File not found: {reference_key}")
        return self.__start_check_job(json_body, DocCheckType.CONSISTENCY)
    
    @result_handler
    def start_typo_check_job(self, json_body):
        validate(event=json_body, schema=check_document_typo_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_DOCUMENT_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")
        return self.__start_check_job(json_body, DocCheckType.TYPO)
        

    def __start_check_job(self, json_body, check_type):
        message_body = DocCheckQueueMessageBody(
            check_type=check_type.value, payload=json_body
        )

        send_message_result = self.queueing_client.send_message(
            self.SQS_DOC_CHECK_QUEUE_NAME, json.dumps(asdict(message_body))
        )

        job_id = send_message_result.get("MessageId", "")

        if job_id:
            job = JobModel(job_id=job_id, status=JobStatus.PENDING.value)
            job.save()

        return StartDocCheckJobResult(job_id=job_id)
    
    @result_handler
    def confirm_check_job(self, query_params):
        job_id = query_params["job_id"]
        job = self.job_repository.find_by_job_id(job_id)
        if not job:
            raise Exception(f"Job not found: {job_id}")
        if job.status == JobStatus.COMPLETED.value:
            payload_json = json.loads(job.payload)
            job.delete()
            return ConfirmDocCheckJobResult(
                status=job.status, payload=payload_json
            )
        elif job.status == JobStatus.FAILED.value:
            job.delete()
            return ConfirmDocCheckJobResult(status=job.status)
        else:
            return ConfirmDocCheckJobResult(status=job.status)

    @result_handler
    def handle_doc_check_request(self, job_id, json_body):
        job = JobModel(job_id=job_id, status=JobStatus.IN_PROGRESS.value)
        job.save()

        try:
            if json_body["check_type"] == DocCheckType.CHECKLIST.value:
                check_document_result = self.check_checklist(json_body["payload"])
            elif json_body["check_type"] == DocCheckType.CONSISTENCY.value:
                check_document_result = self.check_consistency(json_body["payload"])
            elif json_body["check_type"] == DocCheckType.TYPO.value:
                check_document_result = self.check_typo(json_body["payload"])
            else:
                raise Exception(f"Unsupported check type: {json_body['check_type']}")
            job.payload = json.dumps(check_document_result.body, ensure_ascii=False)
            print(job.payload)
            job.status = JobStatus.COMPLETED.value
            job.save()

        except Exception as e:
            job.status = JobStatus.FAILED.value
            job.save()
            raise e

    def __extract_text(self, target_key):
        if file_util.is_pdf(target_key):
            return self.__extract_text_from_pdf(target_key)
        elif file_util.is_word(target_key):
            return self.__extract_text_from_word(target_key)
        else:
            raise Exception(f"Unsupported file type: {target_key}")

    def __extract_text_from_pdf(self, target_key):
        pdf_obj = self.storage_client.get_object(
            bucket=self.S3_DOCUMENT_BUCKET_NAME, key=target_key
        )
        pdf = pypdfium2.PdfDocument(BytesIO(pdf_obj))
        text = ""
        for page in pdf:
            textpage = page.get_textpage()
            page_text = textpage.get_text_range().replace("\n", " ").replace("\r", "")
            text += page_text
        return text

    def __extract_text_from_word(self, target_key):

        doc_obj = self.storage_client.get_object(
            bucket=self.S3_DOCUMENT_BUCKET_NAME, key=target_key
        )
        doc = docx.Document(BytesIO(doc_obj))
        full_text = ""
        content = doc.iter_inner_content()
        for element in content:
            if isinstance(element, docx.table.Table):
                tbl = Element("table")
                for row in element.rows:
                    merged_cell_count = 0
                    tr = SubElement(tbl, "tr")
                    for cell in row.cells:
                        if cell.grid_span > 1:
                            merged_cell_count += 1
                            if merged_cell_count < cell.grid_span:
                                continue
                            td = SubElement(tr, "td", colspan=str(cell.grid_span))
                            merged_cell_count = 0
                        else:
                            td = SubElement(tr, "td")
                        td.text = cell.text.replace("\n", " ").replace("\r", "")
                full_text += tostring(tbl, encoding="unicode")

            elif isinstance(element, docx.text.paragraph.Paragraph):
                full_text += element.text.replace("\n", " ").replace("\r", "")

        return full_text
