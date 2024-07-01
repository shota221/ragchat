from injector import singleton

@singleton
class ProductRepository:
    def __init__(self, dynamodb=None):
        # self.dynamodb = dynamodb or boto3.resource('dynamodb')
        # self.table = self.dynamodb.Table('products')\
        pass

    def get_product(self, product_id):
        # response = self.table.get_item(Key={'product_id': product_id})
        # return response.get('Item')
        return {"product_id": product_id, "name": f"Product {product_id}"}
    
    def get_products(self):
        # response = self.table.scan()
        # return response.get('Items')
        return [{"product_id": "1", "name": "Product 1"}, {"product_id": "2", "name": "Product 2"}]

    def create_product(self, json_body):
        # self.table.put_item(Item=json_body)
        return json_body