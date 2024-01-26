#!/usr/bin/env python3
# @github.com/motebaya - 26.01.2023
# controller main
# file: app/controllers/Main.py

import base64, json
from . import Controller
from typing import Optional, Any, Dict
from string import ascii_uppercase

class Main(Controller):
    @staticmethod
    def index(data: Optional[Dict[str, Any]] = {}) -> str:
        return Main.views(
            "index-hanime.html", {
                "letters": ascii_uppercase,
                **data
            })

    @staticmethod
    def hanimelists(data: Optional[Dict[str, Any]] = {}) -> str:
        return Main.views(
            "hanime-lists.html", {
                "tobase64": base64.b64encode,
                "tojson": json.loads,
                **data
            }
        )
    
    @staticmethod
    def hanimedownload(data: Optional[Dict[str, Any]] = {}) -> str:
        return Main.views(
            "hanime-download.html", {
                "tojson": json.loads,
                "tobase64": base64.b64encode,
                **data
            })
    
    @staticmethod
    def hanimeinfo(data: Optional[Dict[str, Any]] = {}) -> str:
        return Main.views("hanime-info.html", {
            "tobase64": base64.b64encode,
            **data
        })
    
    @staticmethod
    def genre_list(data: Optional[Dict[str, Any]] = {}) -> str:
        return Main.views(
            "genres-list.html", data
        )