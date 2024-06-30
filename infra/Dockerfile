FROM python:3.12-alpine
COPY ./infra/start_local_server.sh /start_local_server.sh
RUN pip install chalice pytest
ARG APP_NAME
WORKDIR /app/${APP_NAME}
CMD ["/bin/sh", "/start_local_server.sh"]