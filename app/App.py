#!/usr/bin/python
# @github.com/motebaya - 12.01.2023
# flask main app.

import os
from app.config import Config
from flask_minify import Minify
from flask import (
    Flask
)

app = Flask(__name__,
    template_folder="views",
    static_url_path="",
    static_folder=os.path.realpath(os.path.join(
        os.path.dirname(__file__), "../public"
    )),
)
app.config.from_object(Config)
Minify(app=app, html=True, js=True, cssless=True)
