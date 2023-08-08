#!/usr/bin/env python3
"""
author: @github.com/motebaya
date: 14.06.2023 - 1:34 PM
file: __init__
"""
from httpx import AsyncClient, URL
from typing import Tuple, Dict, Union
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .logger import logger, logging
from rich.console import Console
from rich.panel import Panel
from time import ctime as current_time
import json, os, re

class Request(AsyncClient):
    def __init__(self) -> None:
        super().__init__()
        self.base_url: URL = URL('https://nekopoi.care')
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'

        # default db path for json and etc.
        self.db_path: str = os.path.join(os.path.realpath("./database/"), "nekopoi.json")
        self.base_dir: str = os.path.dirname(self.db_path) # avoid deleting folder database.
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)

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

    def load_db(self) -> dict:
        # DRY
        return json.loads(open(
            self.db_path
        ).read())

    def show_info(self, data: dict, title: str = None) -> None:
        """
        show info to table.
        """
        Console().print(
            Panel.fit(
                '\n'.join(map(
                    lambda x: f"[green]{x[0].title()}: [white]{x[1]}",
                    dict(sorted(
                        data.items()
                    )).items()
                )), 
                title="[white] information" if not title else title,
                border_style="blue"
            )
        )

    def show_message(self, msg: str):
        """
        custom message
        """
        Console().print(
            "[cyan] {}[reset] {}".format(
                current_time().split()[-2], msg
            ), style="not bold"
        )

    def dbNotEmpty(self) -> Union[bool, None]:
        """
        return True if database is not empty and vice versa.
        """
        if os.path.exists(self.db_path):
            return os.path.getsize(
                self.db_path
            ) >= 1
        return None

    def savedata(self, data: dict) -> None:
        """
        save json data list to file. [overwrite = True]
        """
        if self.dbNotEmpty(): # file exist and not empty, i just send a warning.
            logger.warning("overwriting existing database:: {}".format(
                os.path.basename(self.db_path)
            ))

            """
            IF db not empty and length one of new data more than old data.
            this will be change it. and if not, it will only save old data.
            """
            db = self.load_db()
            for key in data.keys():
                if len(data[key]) >= len(db[key]):
                    db[key] = data[key]
            data = db

        # Save new db
        with open(self.db_path, "w") as f:
            f.write(
                json.dumps(
                    data, indent=2
                ))
        
        self.show_info({
            'message': 'DB saved as -> {}'.format(
                self.db_path
            ),
            'hentai length': "{} items".format(str(len(
                data.get('hentai_list')
            ))),
            'jav length': "{} items".format(str(len(
                data.get('jav_list')
            ))),
            'jav thumbnail ': "{}/jav/thumbnail".format(
                self.base_dir
            ),
            'hentai thumbnail/cover': "{}/hentai/(cover/thumbnail)".format(
                self.base_dir
            )
        }, '[green][bold] DB Information [/bold]')
