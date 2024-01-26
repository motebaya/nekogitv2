#!/usr/bin/python3
# @github.com/motebaya - 12.01.2023
# flask configuration, it's more easier to maintainable
# cc: https://flask.palletsprojects.com/en/3.0.x/api/#flask.Config.from_object

import os, secrets
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.realpath(os.path.join(
    os.path.dirname(__file__), "../.env"
)))

class Config:
    HOST = os.environ.get("HOST") or "0.0.0.0"
    PORT = os.environ.get("PORT") or 5000
    DEBUG = os.environ.get('DEBUG').__str__().lower() == "true"
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(16)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DBPATH") or "sqlite:///{}".format(
        os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                "models/database/nekodata.db"
            )
        )
    )