from boto3.session import Session
from chalice import Chalice

app = Chalice(app_name='test-websockets')
app.experimental_feature_flags.update([
    'WEBSOCKETS',
])
app.websocket_api.session = Session()


@app.on_ws_message()
def message(event):
    app.websocket_api.send(event.connection_id, 'I got your message!')


# import boto3
# from os import environ
# from logging import getLevelName
# from boto3.session import Session
# from chalice import Chalice
# from chalice import WebsocketDisconnectedError
# from chalicelib import hooks
# from chalicelib import routes

# app = Chalice(app_name="sample-app")

# # websocket関連がBlueprintで定義できないため、Chaliceのappに直接設定
# app.experimental_feature_flags.update({"WEBSOCKETS"})
# app.websocket_api.session = Session()

# app.log.setLevel(getLevelName(environ.get("LOG_LEVEL", "INFO")))
# # app.register_blueprint(routes.app)
# # app.register_blueprint(hooks.app)

# @app.on_ws_message()
# def message(event):
#     try:
#         app.websocket_api.send(event.connection_id, event.body)
#     except WebsocketDisconnectedError as e:
#         print(f'Got error: {e}')

# # The view function above will return {"hello": "world"}
# # whenever you make an HTTP GET request to '/'.
# #
# # Here are a few more examples:
# #
# # @app.route('/hello/{name}')
# # def hello_name(name):
# #    # '/hello/james' -> {"hello": "james"}
# #    return {'hello': name}
# #
# # @app.route('/users', methods=['POST'])
# # def create_user():
# #     # This is the JSON body the user sent in their POST request.
# #     user_as_json = app.current_request.json_body
# #     # We'll echo the json body back to the user in a 'user' key.
# #     return {'user': user_as_json}
# #
# # See the README documentation for more examples.
# #
