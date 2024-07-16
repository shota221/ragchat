import os
import json
from io import BytesIO
import pypdfium2
from injector import inject
from chalicelib.clients.storage_client import StorageClient
from chalicelib.helper import file_util


class FileService:
    S3_SOURCE_BUCKET_NAME = os.environ["S3_SOURCE_BUCKET_NAME"]
    S3_DESTINATION_BUCKET_NAME = os.environ["S3_DESTINATION_BUCKET_NAME"]
    CHUNK_SIZE = 4000000
    BUFFER_TEXT_LENGTH = 400
    PDF_EXTENSION = ".pdf"
    DESTINATION_EXTENSION = ".txt"

    @inject
    def __init__(self, storage_client: StorageClient):
        self.storage_client = storage_client

    def preprocess(self, source_key):
        if file_util.is_meta_file(source_key):
            raise Exception(f"Meta file cannot be preprocessed: {source_key}")
        if not self.storage_client.exists(
            bucket=self.S3_SOURCE_BUCKET_NAME, key=source_key
        ):
            raise Exception(f"File not found: {source_key}")
        
        self.__set_preprocessing_flag(source_key)

        try:
            if source_key.endswith(self.PDF_EXTENSION):
                self.__handle_pdf(source_key)
            else:
                self.__handle_others(source_key)
        finally:
            self.__remove_preprocessing_flag(source_key)

    def __handle_others(self, source_key):
        destination_key = (
            f"{file_util.guess_preprocessing_destination_dir(source_key)}{source_key}"
        )
        self.storage_client.copy_object(
            bucket=self.S3_SOURCE_BUCKET_NAME,
            key=source_key,
            destination_bucket=self.S3_DESTINATION_BUCKET_NAME,
            destination_key=destination_key,
        )
        print (f"destination_key: {destination_key} created")
        meta_key = file_util.guess_meta_key_by_destination_key(destination_key)
        tmp_meta_key = file_util.guess_tmp_meta_key(source_key)
        if self.storage_client.exists(
            bucket=self.S3_DESTINATION_BUCKET_NAME, key=tmp_meta_key
        ):
            self.storage_client.copy_object(
                bucket=self.S3_DESTINATION_BUCKET_NAME,
                key=tmp_meta_key,
                destination_bucket=self.S3_DESTINATION_BUCKET_NAME,
                destination_key=meta_key,
            )
            print (f"meta_key: {meta_key} created")
            self.storage_client.delete_object(
                bucket=self.S3_DESTINATION_BUCKET_NAME, key=tmp_meta_key
            )
        elif not self.storage_client.exists(
            bucket=self.S3_DESTINATION_BUCKET_NAME, key=meta_key
        ):
            self.storage_client.put_object(
                bucket=self.S3_DESTINATION_BUCKET_NAME,
                key=meta_key,
                body=json.dumps(file_util.generate_meta(source_key), ensure_ascii=False),
            )
            print (f"meta_key: {meta_key} created")
  

    def __handle_pdf(self, source_key):
        chunk_num = 0
        destination_keys = []
        for chunked_text in self.__text_extractor(
            source_key, self.CHUNK_SIZE, self.BUFFER_TEXT_LENGTH
        ):
            chunk_num += 1
            destination_key = f"{file_util.guess_preprocessing_destination_dir(source_key)}{chunk_num}{self.DESTINATION_EXTENSION}"
            self.storage_client.put_object(
                bucket=self.S3_DESTINATION_BUCKET_NAME,
                key=destination_key,
                body=chunked_text,
            )
            print (f"destination_key: {destination_key} created")
            destination_keys.append(destination_key)

        tmp_meta_key = file_util.guess_tmp_meta_key(source_key)
        if self.storage_client.exists(
            bucket=self.S3_DESTINATION_BUCKET_NAME, key=tmp_meta_key
        ):
            tmp_meta = self.storage_client.get_json_object(
                bucket=self.S3_DESTINATION_BUCKET_NAME, key=tmp_meta_key
            )
            for dest_key in destination_keys:
                meta_key = file_util.guess_meta_key_by_destination_key(dest_key)
                self.storage_client.put_object(
                    bucket=self.S3_DESTINATION_BUCKET_NAME,
                    key=meta_key,
                    body=json.dumps(tmp_meta, ensure_ascii=False),
                )
                print (f"meta_key: {meta_key} created")
            self.storage_client.delete_object(
                bucket=self.S3_DESTINATION_BUCKET_NAME, key=tmp_meta_key
            )
        elif not self.storage_client.exists_dir(
            bucket=self.S3_DESTINATION_BUCKET_NAME,
            dir=file_util.guess_meta_dir(source_key),
        ):
            for dest_key in destination_keys:
                meta_key = file_util.guess_meta_key_by_destination_key(dest_key)
                self.storage_client.put_object(
                    bucket=self.S3_DESTINATION_BUCKET_NAME,
                    key=meta_key,
                    body=json.dumps(file_util.generate_meta(source_key), ensure_ascii=False),
                )
                print (f"meta_key: {meta_key} created")
        else:
            meta = self.storage_client.get_json_object(
                bucket=self.S3_DESTINATION_BUCKET_NAME,
                key=file_util.guess_meta_key_by_destination_key(destination_keys[0]),
            ) or file_util.generate_meta(source_key)
            for dest_key in destination_keys:
                meta_key = file_util.guess_meta_key_by_destination_key(dest_key)
                if self.storage_client.exists(
                    bucket=self.S3_DESTINATION_BUCKET_NAME, key=meta_key
                ):
                    continue

                self.storage_client.put_object(
                    bucket=self.S3_DESTINATION_BUCKET_NAME,
                    key=meta_key,
                    body=json.dumps(meta, ensure_ascii=False),
                )

    def clean_up(self, source_key):
        if file_util.is_meta_file(source_key):
            return
        if self.storage_client.exists(
            bucket=self.S3_SOURCE_BUCKET_NAME, key=source_key
        ):
            print(f"source_key: {source_key} exists")
            return

        destination_dir = file_util.guess_preprocessing_destination_dir(source_key)
        meta_file_dir = file_util.guess_meta_dir(source_key)

        self.storage_client.delete_objects(
            self.S3_DESTINATION_BUCKET_NAME, destination_dir
        )
        print(f"destination_dir: {destination_dir} removed")

        self.storage_client.delete_objects(
            self.S3_DESTINATION_BUCKET_NAME, meta_file_dir
        )
        print(f"meta_file_dir: {meta_file_dir} removed")

        return

    def preprocess_all(self):
        for obj in self.storage_client.list_objects(bucket=self.S3_SOURCE_BUCKET_NAME):
            if file_util.is_meta_object(obj["Key"]):
                continue
            self.preprocess(obj["Key"])

    def __text_extractor(self, source_key, chunk_size, buffer_text_length):
        pdf_obj = self.storage_client.get_pdf_object(
            bucket=self.S3_SOURCE_BUCKET_NAME, key=source_key
        )
        pdf = pypdfium2.PdfDocument(BytesIO(pdf_obj))
        pages_text = ""
        buffer_text = ""
        pages_len = 0
        for page in pdf:
            textpage = page.get_textpage()
            text = textpage.get_text_range().replace("\n", " ").replace("\r", "")
            page_len = len(text.encode("utf-8"))
            if pages_len + page_len > chunk_size:
                yield pages_text
                buffer_text = pages_text[-buffer_text_length:]
                pages_text = buffer_text
                pages_len = len(pages_text.encode("utf-8"))
            pages_text += text
            pages_len += page_len
        yield pages_text


    def __set_preprocessing_flag(self, source_key):
        self.storage_client.put_object(
            bucket=self.S3_DESTINATION_BUCKET_NAME,
            key=file_util.guess_preprocessing_flag_key(source_key),
            body="",
        )

    def __remove_preprocessing_flag(self, source_key):
        self.storage_client.delete_object(
            bucket=self.S3_DESTINATION_BUCKET_NAME,
            key=file_util.guess_preprocessing_flag_key(source_key),
        )