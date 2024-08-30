from os import environ
import json
from logging import getLogger, getLevelName
from injector import Injector
import boto3
from chalicelib.services.search_engine_service import SearchEngineService
from chalicelib.services.inquiry_service import InquiryService
from chalicelib.services.file_service import FileService
from chalicelib.services.document_service import DocumentService
from chalicelib.services.file_attr_service import FileAttrService
from chalicelib.helper.file_util import INHIBITOR_FILE_PREFIX
from chalice import Chalice, WebsocketDisconnectedError

app = Chalice(app_name="ragchat")

app.websocket_api.session = boto3.Session()
app.experimental_feature_flags.update({
    'WEBSOCKETS',
})

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

# @app.route("/files/_preprocess", methods=["POST"])
# def preprocess_files():
#     return injector.get(FileService).preprocess_all()

# @app.route("/documents/check", methods=["POST"])
# def check_document():
#     return injector.get(DocumentService).check(app.current_request.json_body)

# @app.route("/documents/check_job/start", methods=["POST"])
# def start_check_document_job():
#     return injector.get(DocumentService).start_check_job(app.current_request.json_body)

# @app.route("/documents/check_job/stop", methods=["POST"])
# def stop_check_document_job():
#     return injector.get(DocumentService).stop_check_job(app.current_request.json_body)

# @app.route("/documents/check_job/confirm", methods=["GET"])
# def get_check_document_job_status():
#     return injector.get(DocumentService).confirm_check_job(app.current_request.query_params)

### checkを分ける場合
@app.route("/documents/checklist_check_job/start", methods=["POST"])
def start_check_document_checklist_job():
    return injector.get(DocumentService).start_checklist_check_job(app.current_request.json_body)

@app.route("/documents/consistency_check_job/start", methods=["POST"])
def start_check_document_consistency_job():
    return injector.get(DocumentService).start_consistency_check_job(app.current_request.json_body)

@app.route("/documents/typo_check_job/start", methods=["POST"])
def start_check_document_typo_job():
    return injector.get(DocumentService).start_typo_check_job(app.current_request.json_body)

@app.route("/documents/checklist_check_job/confirm", methods=["GET"])
def confirm_check_document_checklist_job():
    return injector.get(DocumentService).confirm_check_job(app.current_request.query_params)

@app.route("/documents/consistency_check_job/confirm", methods=["GET"])
def confirm_check_document_consistency_job():
    return injector.get(DocumentService).confirm_check_job(app.current_request.query_params)

@app.route("/documents/typo_check_job/confirm", methods=["GET"])
def confirm_check_document_typo():
    return injector.get(DocumentService).confirm_check_job(app.current_request.query_params)

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
    injector.get(SearchEngineService).dispatch_pending_sync_job()

@app.on_sqs_message(queue=environ["SQS_DOC_CHECK_QUEUE_NAME"])
def on_sqs_doc_check_request(event):
    for record in event:
        # record.bodyの最大長は256KB
        injector.get(DocumentService).handle_doc_check_request(record.to_dict().get('messageId'), json.loads(record.body))


######################
# websocket          #
######################

@app.on_ws_message()
def message(event):
    try:
        json_body=json.loads(event.body)
        if json_body.get('action') == 'sendMessage':
            for token in injector.get(InquiryService).stream(json_body.get('data')):
                app.websocket_api.send(event.connection_id, token)
    except WebsocketDisconnectedError as e:
        print(f'Got error: {e}')
    