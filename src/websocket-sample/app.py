from boto3.session import Session

from chalice import Chalice
from chalice import WebsocketDisconnectedError

app = Chalice(app_name='websocket-sample')
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
    