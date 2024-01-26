#!/usr/bin/python3
# @github.com/motebaya - 15.01.2024
# init controller
# file: app/controllers/__init__.py

from flask import render_template
from typing import Any, Dict, Optional

class Controller:
    @staticmethod
    def views(template: str, data: Optional[Dict[str, Any]] = {}) -> str:
        return render_template(
            template, **data
            
        )