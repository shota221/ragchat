from os import environ
from logging import getLogger, getLevelName
from boto3.session import Session
from chalice import Chalice
from chalice import Rate
from chalice import WebsocketDisconnectedError
from injector import Injector
from chalicelib.services.product_service import ProductService

app = Chalice(app_name="sample-app")

logger = getLogger(__name__)
logger.setLevel(getLevelName(environ.get("LOG_LEVEL", "DEBUG")))

injector = Injector()

######################
# routes definition  #
######################
product_service = injector.get(ProductService)

@app.route("/products", methods=["GET"])
def list_products():
    return product_service.get_products()


@app.route("/products", methods=["POST"])
def create_product():
    return product_service.create_product(app.current_request.json_body)

@app.route("/products/{product_id}", methods=["GET"])
def get_product(product_id):
    return product_service.get_product(product_id)


######################
# scheduled events   #
######################

@app.schedule(Rate(1, unit=Rate.MINUTES))
def scheduled_log(event):
    return {"message": "Scheduled event triggered"}


######################
# event handlers     #
######################

@app.on_sns_message(topic="mytopic")
def sns_message_handler(event):
    return {"message": event.message}

@app.on_s3_event(bucket="mybucket")
def s3_event_handler(event):
    return {"Records": event.to_dict()}


#############
# websocket #
#############

app.websocket_api.session = Session()
app.experimental_feature_flags.update({
    'WEBSOCKETS',
})

@app.on_ws_message()
def message(event):
    try:
        print(f"Received message: {event.body}")
        app.websocket_api.send(event.connection_id, event.body)
    except WebsocketDisconnectedError as e:
        print(f'Got error: {e}')