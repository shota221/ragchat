from logging import getLogger
from http import HTTPStatus
from dataclasses import asdict, is_dataclass
from aws_lambda_powertools.utilities.validation import SchemaValidationError
from chalice import Response

logger = getLogger(__name__)

def result_handler(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            body = asdict(result) if is_dataclass(result) else result
            return Response(
                status_code=HTTPStatus.OK,
                body=body,
            )
        except SchemaValidationError as e:
            return Response(
                status_code=HTTPStatus.BAD_REQUEST,
                body={"error": str(e)},
            )
        except Exception as e:
            logger.error(
                "An error occurred while processing request: %s", str(e)
            )
            return Response(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                body={"error": str(e)},
            )
    return wrapper

