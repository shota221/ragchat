from os import environ
from logging import getLogger, getLevelName
from injector import Injector
from chalicelib.services.search_engine_service import SearchEngineService
from chalice import Chalice
from chalice import Response

app = Chalice(app_name="ragchat")

logger = getLogger(__name__)
logger.setLevel(getLevelName(environ.get("LOG_LEVEL", "DEBUG")))

injector = Injector()

######################
# routes definition  #
######################

# todo: error handling
@app.route("/search-engine/sync-job/request", methods=["POST"])
def request_search_engine_sync_job():
    try: 
        result = injector.get(SearchEngineService).request_sync_job()

        return Response(
            status_code=200,
            body=result,
        )
    
    except Exception as e:
        logger.error(
            "An error occurred while requesting search engine sync job: %s", str(e)
        )
        return Response(
            status_code=500,
            body={"error": str(e)},
        )


@app.route("/search-engine/sync-job/confirm", methods=["GET"])
def confirm_search_engine_sync_job():
    try: 
        result = injector.get(SearchEngineService).confirm_sync_job()
        return Response(
            status_code=200,
            body=result,
        )
    
    except Exception as e:
        logger.error(
            "An error occurred while confirming search engine sync job: %s", str(e)
        )
        return Response(
            status_code=500,
            body={"error": str(e)},
        )
