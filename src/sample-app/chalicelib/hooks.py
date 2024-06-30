from chalice import Blueprint
from chalice import WebsocketDisconnectedError

app = Blueprint(__name__)


# @app.on_ws_connect()
# def connect(event):
#     print(f"New connection: {event.connection_id}")


@app.on_ws_message()
def message(event):
    try:
        app.websocket_api.send(event.connection_id, event.body)
    except WebsocketDisconnectedError as e:
        print(f'Got error: {e}')
    

# @app.on_ws_disconnect()
# def disconnect(event):
#     print(f"{event.connection_id} disconnected")


# @app.on_sns_message(topic="mytopic")
# def sns_message_handler(event):
#     return {"message": event.message}
