from aws_lambda_powertools.utilities.validation import validate
from chalice import Response
from chalicelib.repositories.product_repository import ProductRepository
from chalicelib.schemas import create_product_schema


class ProductService:
    def __init__(self):
        self.product_repository = ProductRepository()

    def get_products(self):
        return self.product_repository.get_products()

    def get_product(self, product_id):
        return self.product_repository.get_product(product_id)

    def create_product(self, json_body):
        try:
            validate(event=json_body, schema=create_product_schema.INPUT)            
            return self.product_repository.create_product(json_body)
        except Exception as e:
            return Response(
                status_code=400,
                body={"error": str(e)},
            )
