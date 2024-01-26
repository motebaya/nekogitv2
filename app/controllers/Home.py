#!/usr/bin/python3
# @github.com/motebaya - 23.01.2024
# home controller
# file: app/controllers/Home.py

from . import Controller
from typing import Optional, Dict, Any

class Home(Controller):
    @staticmethod
    def index(data: Optional[Dict[str, Any]] = {}) -> str:
        return Home.views("index.html", data)
    
    @staticmethod
    def notFound(arg: Optional[Any] = '', data: Optional[Dict[str, Any]] = {}) -> str:
        return Home.views("404.html", data)