#!/bin/bash

cd /app

if [ -z "$(ls -A $APP_NAME)" ]; then
  rm -rf $APP_NAME
  chalice new-project $APP_NAME
  chmod -R 777 $APP_NAME
fi

cd $APP_NAME
. requirements.txt
pip install -r requirements.txt

# ローカルサーバーを起動
chalice local --host=0.0.0.0 --port=8000 --stage local
