import os
import json
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
from chalicelib.dataclasses.check_document_result import (
    ChecklistItem,
    TyposItem,
    CheckDocumentResult,
)
from chalicelib.dataclasses.start_doc_check_job_result import StartDocCheckJobResult
from chalicelib.dataclasses.confirm_doc_check_job_result import ConfirmDocCheckJobResult
from chalicelib.schemas import check_document_schema, generation_ai_doc_check_schema
from chalicelib.models.job_model import JobModel
from chalicelib.repositories.job_repository import JobRepository
from chalicelib.enums.job_status import JobStatus


class DocumentService:
    S3_CHECK_TARGET_BUCKET_NAME = os.environ["S3_CHECK_TARGET_BUCKET_NAME"]
    SQS_DOC_CHECK_QUEUE_NAME = os.environ["SQS_DOC_CHECK_QUEUE_NAME"]
    PDF_EXTENSION = ".pdf"
    WORD_EXTENSION = ".docx"
    ASSISTANT_TEXT_PREFIX = "{"
    ASSISTANT_TEXT_SUFFIX = "}"
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
    def check(self, json_body):
        validate(event=json_body, schema=check_document_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_CHECK_TARGET_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")

        document = self.__extract_text(target_key)
        checklist = json_body["checklist"]
        summary_policy = json_body["summary_policy"]

        checklist_early_head, checklist_late_tail = checklist[:self.CHECKLIST_SIZE_THRESHOLD], checklist[self.CHECKLIST_SIZE_THRESHOLD:]

        res = self.__assistant_check_result(document, checklist_early_head, summary_policy)

        result = CheckDocumentResult(
            checklist=[
                ChecklistItem(
                    id=item["id"],
                    result=item["res"],
                    quotes=item["qot"],
                    references=item["ref"],
                    comment=item["cmt"],
                )
                for item in res["checklist"]
            ],
            typos=[
                TyposItem(
                    original=item["org"],
                    corrected=item["cor"],
                )
                for item in res["typos"] if item["org"] != item["cor"]
            ],
            summary=res["summary"],
        )


        for i in range(0, len(checklist_late_tail), self.CHECKLIST_CHUNK_SIZE):
            res = self.__assistant_check_result_checklist_only(document, checklist_late_tail[i:i+self.CHECKLIST_CHUNK_SIZE])
            result.checklist.extend([
                ChecklistItem(
                    id=item["id"],
                    result=item["res"],
                    quotes=item["qot"],
                    references=item["ref"],
                    comment=item["cmt"],
                )
                for item in res["checklist"]
            ])

        return result
    
    def __assistant_check_result(self, document:str, checklist, summary_policy:str):
        policy = json.dumps(
            {"summary": summary_policy},
            ensure_ascii=False,
        )
        checklist_str = json.dumps(checklist, ensure_ascii=False)
        prompt = self.prompt_builder.build_doc_check_prompt(document, checklist_str, policy)
        assistant_text = self.ASSISTANT_TEXT_PREFIX
        assistant_text = assistant_text + self.generation_ai_client.generate_message(
            prompt, assistant_text, max_tokens=8192, top_p=0.1
        )
        assistant_text = assistant_text[
            : assistant_text.rfind(self.ASSISTANT_TEXT_SUFFIX) + 1
        ]
        result = json.loads(assistant_text)
        validate(event=result, schema=generation_ai_doc_check_schema.ASSISTANT)

        return result

    def __assistant_check_result_checklist_only(self, document:str, checklist):
        checklist_str = json.dumps(checklist, ensure_ascii=False)
        prompt = self.prompt_builder.build_doc_check_prompt(document, checklist_str, section="DOC_CHECK_CHECKLIST_ONLY")
        assistant_text = self.ASSISTANT_TEXT_PREFIX
        assistant_text = assistant_text + self.generation_ai_client.generate_message(
            prompt, assistant_text, max_tokens=8192, top_p=0.1
        )
        assistant_text = assistant_text[
            : assistant_text.rfind(self.ASSISTANT_TEXT_SUFFIX) + 1
        ]
        result = json.loads(assistant_text)
        validate(event=result, schema=generation_ai_doc_check_schema.ASSISTANT_CHECKLIST_ONLY)

        return result


    @result_handler
    def start_check_job(self, json_body):
        validate(event=json_body, schema=check_document_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_CHECK_TARGET_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")
        send_message_result = self.queueing_client.send_message(
            self.SQS_DOC_CHECK_QUEUE_NAME, json.dumps(json_body)
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
            check_document_result = CheckDocumentResult(
                checklist=[
                    ChecklistItem(
                        id=item["id"],
                        result=item["result"],
                        quotes=item["quotes"],
                        references=item["references"],
                        comment=item["comment"],
                    )
                    for item in payload_json["checklist"]
                ],
                typos=[
                    TyposItem(
                        original=item["original"],
                        corrected=item["corrected"],
                    )
                    for item in payload_json["typos"]
                ],
                summary=payload_json["summary"],
            )
            job.delete()
            return ConfirmDocCheckJobResult(
                status=job.status, payload=check_document_result
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
            check_document_result = self.check(json_body)
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
            bucket=self.S3_CHECK_TARGET_BUCKET_NAME, key=target_key
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
            bucket=self.S3_CHECK_TARGET_BUCKET_NAME, key=target_key
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
