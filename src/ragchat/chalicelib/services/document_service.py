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
from chalicelib.clients.storage_client import StorageClient
from chalicelib.dataclasses.check_document_result import ChecklistItem, TyposItem, CheckDocumentResult
from chalicelib.schemas import check_document_schema, generation_ai_doc_check_schema


class DocumentService:
    S3_CHECK_TARGET_BUCKET_NAME = os.environ["S3_CHECK_TARGET_BUCKET_NAME"]
    PDF_EXTENSION = ".pdf"
    WORD_EXTENSION = ".docx"
    ASSISTANT_TEXT_PREFIX = "{"
    ASSISTANT_TEXT_SUFFIX = "}"

    @inject
    def __init__(
        self, generation_ai_client: GenerationAiClient, storage_client: StorageClient
    ):
        self.generation_ai_client = generation_ai_client
        self.storage_client = storage_client

    @result_handler
    def check(self, json_body):
        validate(event=json_body, schema=check_document_schema.INPUT)
        target_key = json_body["target_key"]
        if not self.storage_client.exists(self.S3_CHECK_TARGET_BUCKET_NAME, target_key):
            raise Exception(f"File not found: {target_key}")

        document = self.__extract_text(target_key)
        checklist = json.dumps(json_body["checklist"], ensure_ascii=False)
        summary_policy = json_body["summary_policy"]
        policy = json.dumps(
            {"summary": summary_policy},
            ensure_ascii=False,
        )

        prompt_builder = PromptBuilder()
        prompt = prompt_builder.build_doc_check_prompt(document, checklist, policy)

        assistant_text = self.ASSISTANT_TEXT_PREFIX

        assistant_text = assistant_text + self.generation_ai_client.generate_message(
            prompt, assistant_text, max_tokens=8192, top_p=0.1
        )

        assistant_text = assistant_text[:assistant_text.rfind(self.ASSISTANT_TEXT_SUFFIX) + 1]

        res = json.loads(assistant_text)

        validate(event=res, schema=generation_ai_doc_check_schema.ASSISTANT)

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
                for item in res["typos"]
            ],
            summary=res["summary"],
        )

        return result

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
