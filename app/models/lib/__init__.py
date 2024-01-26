#!/usr/bin/python3
# github.com/motebaya - 20.01.2023
# init module
# file: app/models/lib/__init__.py

from httpx import Client
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from ..helpers import Logger

class Init:
    def __init__(self, verbose: bool) -> None:
        self.verbose = verbose
        self.logger = Logger.getLogger("debug" if self.verbose else "info")
    
    def createSession(self, host: Optional[str] = '', config: Optional[Dict[str, Any]] = {}) -> Client:
        if config and not host:
            return Client(**config)
        return Client(
            base_url=host, headers={
                "Host": urlparse(host).hostname,
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
        )

    def parse(self, raw: str) -> BeautifulSoup:
        """parse raw html with bs4

        :param str raw: request response
        :return BeautifulSoup: result
        """
        return BeautifulSoup(
            raw if not hasattr(raw, 'text') else raw.text,
            "html.parser"
        )

    def get_id(self, url: str) -> str:
        """get string id from url

        :param str url: url
        :return str: result
        """
        return urlparse(url).path.strip('/'
            ).split('/', 1)[-1]