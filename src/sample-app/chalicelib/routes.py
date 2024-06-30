
from chalice import Blueprint
from chalicelib.services.product_service import ProductService

app = Blueprint(__name__)


@app.route("/sample-app")
def index():
    app.log.debug("This is a debug message")
    return {"hello": "world"}


# @app.route("/products", methods=["GET"])
# def list_products():
#     return ProductService().get_products()


# @app.route("/products", methods=["POST"])
# def create_product():
#     return ProductService().create_product(app.current_request.json_body)


# @app.route("/products/{product_id}", methods=["GET"])
# def get_product(product_id):
#     return ProductService().get_product(product_id)
