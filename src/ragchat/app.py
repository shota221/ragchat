from os import environ
from logging import getLogger, getLevelName
from injector import Injector
from chalicelib.services.search_engine_service import SearchEngineService
from chalicelib.services.inquiry_service import InquiryService
from chalicelib.services.file_service import FileService
from chalicelib.services.file_attr_service import FileAttrService
from chalicelib.helper.file_util import INHIBITOR_FILE_PREFIX
from chalice import Chalice

app = Chalice(app_name="ragchat")

logger = getLogger(__name__)
logger.setLevel(getLevelName(environ.get("LOG_LEVEL", "DEBUG")))

injector = Injector()

######################
# routes definition  #
######################

@app.route("/search-engine/sync-job/request", methods=["POST"])
def request_search_engine_sync_job():
    return injector.get(SearchEngineService).request_sync_job()

@app.route("/search-engine/sync-job/confirm", methods=["GET"])
def confirm_search_engine_sync_job():
    return injector.get(SearchEngineService).confirm_sync_job()

@app.route("/inquiries", methods=["POST"])
def send_inquiry():
    return injector.get(InquiryService).send(app.current_request.json_body)

@app.route("/inquiries/embedding", methods=["POST"])
def generate_embedding():
    return injector.get(InquiryService).generate_embedding(app.current_request.json_body)

@app.route("/file_attrs", methods=["PUT"])
def update_file_attr():
    return injector.get(FileAttrService).update(app.current_request.json_body)

@app.route("/files/_preprocess", methods=["POST"])
def preprocess_files():
    return injector.get(FileService).preprocess_all()


######################
# event handlers     #
######################

@app.on_s3_event(bucket=environ["S3_SOURCE_BUCKET_NAME"], events=["s3:ObjectRemoved:Delete"])
def on_s3_object_removed(event):
    logger.info(f"on_s3_object_removed: {event.key}")
    injector.get(FileService).clean_up(event.key)

@app.on_s3_event(bucket=environ["S3_SOURCE_BUCKET_NAME"], events=["s3:ObjectCreated:*"])
def on_s3_object_created(event):
    logger.info(f"on_s3_object_created: {event.key}")
    injector.get(FileService).preprocess(event.key)

@app.on_s3_event(bucket=environ["S3_DESTINATION_BUCKET_NAME"], events=["s3:ObjectRemoved:Delete"], prefix=INHIBITOR_FILE_PREFIX)
def on_inhibitor_removed(event):
    logger.info(f"on_inhibitor_removed: {event.key}")
    injector.get(SearchEngineService).check_pending_sync_job()