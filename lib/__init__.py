#!/usr/bin/env python3
"""
author: @github.com/motebaya
date: 14.06.2023 - 1:34 PM
file: __init__
"""
from httpx import AsyncClient
from typing import Tuple, Dict
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .logger import logger
import json, os, re

class Request(AsyncClient):
    def __init__(self) -> None:
        super().__init__()
        self.base_url: str = 'https://nekopoi.care'
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'

class Base(Request):

    def strip_host(self, url: str) -> str:
        return re.sub(r"https?://[^/]+", "", url)

    def get_id(self, url: str) -> str:
        return urlparse(
                url
            ).path.strip('/'
        ).split('/', 1)[-1]

    def parse(self, text: str) -> BeautifulSoup:
        return BeautifulSoup(
            text, 'html.parser'
        )

    def set_netloc(self, url: str) -> None:
        netloc = urlparse(url).netloc
        if netloc not in str(self.base_url):
            self.base_url = self.base_url.__str__().replace(
                urlparse(
                    self.base_url.__str__()
                ).netloc, netloc
            )
            logger.debug(f"host change: {netloc}")
            return
        return

    def get_form_data(self, html: str) -> Tuple[str, Dict[
        str, str
    ]]:
        soup = self.parse(html)
        if (form := soup.find('form')):
            return (
                form.attrs.get('action'), 
                {
                    _.attrs.get('name'): \
                        _.attrs.get('value') \
                    for _ in form.find_all('input')
                }
            )
        return ()

    def savedata(self, to: str, data: list) -> None:
        """
        save json data list to file. [overwrite = True]
        """
        to = os.path.realpath("./database/" + to)
        dbdir = os.path.dirname(to)
        try:
            if not isinstance(data, list):
                data = json.loads(data)

            if not os.path.exists(dbdir):
                logger.debug(f"creating new folder: {dbdir}")
                os.mkdir(dbdir)

            if os.path.exists(to):
                logger.warning(f"overwriting existing content: {to} with length: {len(data)}")

            with open(to, 'w') as f:
                f.write(
                    json.dumps(
                        data, sort_keys=True, indent=1
                    )
                )
            logger.info(f"data saved in: {to} with length: {len(data)}")
            return
        except (TypeError, json.decoder.JSONDecodeError):
            with open(to, 'w') as f:
                f.write(
                    ".cache-{}".format(to)
                )
            logger.info(f"Exception: cache saved in .cache-{to}")

    def showinfo(self, data: dict) -> None:
        """
        show json items as debug
        """
        if isinstance(data, dict):
            for j, k in data.items():
                if j != 'episode':
                    logger.info(
                        f"{j.title()}: {k}"
                    )
                else:
                    continue
        else:
            logger.warning("null") 
            return
