#!/usr/bin/env python3
# author: @github.com/motebaya
# date: 4.6.2023 05:07:13 PM
# file: Rajahentai.py

from . import Base
from .logger import logger
from typing import Generator, Dict, Union, Optional, List
from urllib.parse import urlparse, urlunparse, parse_qs, urljoin, unquote
import re

class Rajahentai(Base):
    def __init__(self) -> None:
        super().__init__()
        self.base_url = "https://rajahentai.xyz"

    async def lewat(self, url):
        page = await self.get("https://rajahentai.xyz/lewat?id=126495")
        return page.text

    """
    get all hentai list: return as generator 
    """
    async def get_hentai_list(self) -> Generator[Dict[str, str], None, None]:
        page = await self.get("/daftar")
        soup = self.parse(page.text)
        if (soralist := soup.find('div', class_='soralist')):
            for i in filter(lambda x: \
                x.attrs.get('href'), 
                    soralist.find_all('a')):
                yield {
                    'title': i.text.strip(),
                    'id': self.get_id(
                        i.attrs.get('href')
                    )
                }
        yield

    """
    get hentai info: []
    """
    async def get_hentai_info(self, id: str) -> Optional[Dict[str,
            Union[str, List[
                Dict[str, str]
            ]
        ]
    ]]:
        page = await self.get(f"/anime/{id}")
        soup = self.parse(page)
        d: Dict[str, Union[
            str, List[Dict[str,
             str]
            ]
        ]] = {}
        if (body := soup.find(class_='postbody')):
            """
            set date & synopsis
            """
            d.update({
                'date': body.find(class_='updated').text, 
                'desc': body.find('p').text
            })

            """
            search cover
            """
            if (img := re.search(
                r"(?P<img>https?\:\/\/[^\"]+?.jpg)",
                    body.find('img').__str__())):
                d['image'] = img.groupdict().get('img')

            """
            table info
            """
            if (info := body.find('table')):
                d.update(dict(map(
                    lambda x: (x.th.text.strip(":"), x.td.text),
                    info.find_all('tr')
                )))

            """
            eps: [title, anime/<id>]
            """
            if (eps := body.find(class_='daftar')):
                d['episode'] = list(map(
                    lambda x: {
                        x[0].__str__(): self.get_id(
                            x[1].a.attrs.get('href')
                        )
                    }, enumerate(
                        eps.find_all('li'), 1
                    )
                ))
            return d
        return None

    """
    get download server list:
    rajahentai.xyz/lewat?id=[id] -> cloudflare turnstill, skip.
    """
    async def get_download_list(self, ideps: str) -> Union[List[Dict[
            str, str]], None]:
        page = await self.get(f"/anime/{ideps}")
        soup = self.parse(page.text)
        if (dl := soup.find_all('a', class_='singledl')):
            return list(map(
                lambda x: {
                    x.text: urljoin(
                        str(self.base_url),
                            x.attrs.get('href'))
                }, filter(
                    lambda x: not x.attrs.get('id'), dl
                )
            ))
        return None

    """
    get redirect for streamsb server
    this will called from separated section, e.g like ouo.io bypasser.
    """
    async def get_redirect(self, url: str) -> str:
        if (re.match(r"^https?:\/\/bokepku\.xyz\/\w+\.php\?id\=[0-9]+$", url)):
            """
            maybe got blocked by cloudflare turnstill
            bokepku.xyz/srvsb.php?id=[id]
            """
            self.set_netloc(url)
            page = await self.get(
                self.strip_host(url),
                follow_redirects=False
            )
            if page.status_code == 302:
                if (location := page.headers.get('Location')):
                    unquoted_url = urlparse(
                        unquote(
                            location
                        )
                    )
                    if unquoted_url.query.strip():
                        redirect_url = parse_qs(
                            unquoted_url.query
                        ).get('s')[0]
                        self.set_netloc(redirect_url)
                        
                        page = await self.get(
                            self.strip_host(redirect_url), follow_redirects=False
                        )
                        if (location := page.headers.get('Location')):
                            return location
                        return None
                    logger.warning("empty query string url: {}".format(urlunparse(unquoted_url)))
                    return None
                logger.warning("no redirect found?: {}".format(url))
                return None
            logger.warning("failed get redirect url: \033[31mcloudflare turnstill blocked.")
        return None
