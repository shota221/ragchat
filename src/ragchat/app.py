from os import environ
from logging import getLogger, getLevelName
from injector import Injector
from chalicelib.services.search_engine_service import SearchEngineService
from chalicelib.services.inquiry_service import InquiryService
from chalicelib.services.file_attr_service import FileAttrService
from chalice import Chalice
from chalice import Response

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

@app.route("/file_attrs/init", methods=["POST"])
def init_file_attr():
    return injector.get(FileAttrService).init()


######################
# event handlers     #
######################

@app.on_s3_event(bucket=environ["S3_BUCKET_NAME"], events=["s3:ObjectRemoved:Delete"])
def on_s3_object_removed(event):
    # オブジェクトキーを取得
    logger.info(f"on_s3_object_removed: {event.key}")
    injector.get(FileAttrService).remove(event.key)

