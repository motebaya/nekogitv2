#!/usr/bin/env python3
# author: @github.com/motebaya
# date: 2023.06.3 04:46:21 PM
# file: Nekopoi.py

from . import Base, urlparse, logger
from typing import Dict, Generator, List, Union, Sequence, Collection
from urllib.parse import unquote
import re

class Nekopoi(Base):

    def __init__(self) -> None:
        super().__init__()

    """
    return async iterator of all hentai list
    """
    async def get_title_list(self, page: str) -> Generator[Dict[str, str], None, None]:
        page = await self.get(f"/{page}-list/")
        soup = self.parse(page.text)
        if (hentai_list := soup.find_all(class_='title-cell')):
            for h in hentai_list:
                yield {
                    "title": h.a.text,
                    "id": self.get_id(
                        h.a.get('href')
                    )
                }
        yield

    """
    get hentai information
    """
    async def get_hentai_info(self, id: str) -> Union[Dict[str, Sequence[Collection[str]]], dict]:
        page = await self.get(f"/hentai/{id}/")
        soup = self.parse(page.text)

        d: Dict[str, Union[str, List[Dict
            [str, Union[str,str]]]]] = {}

        if (s := soup.find(class_='animeinfos')):
            """
            update synopsis and cover
            """
            if (desc := s.find(class_="imgdesc")):
                d.update({
                    "image": desc.img.get('src'),
                    "desc": ''.join(map(
                        lambda x: x.text,
                        desc.find_all('p')
                    ))
                })

            """
            set genre and info
            """
            if (info := s.find(class_='listinfo')):
                for li in \
                    map(lambda x: x.find('b'),
                        info.find_all('li')):
                    if li:
                        k: str = re.sub(r"^\:\s+", "", li.next_sibling.strip())
                        if not k.startswith(':'):
                            d[li.text] = k
                        else:
                            d[li.text] = ", ".join(map(
                                lambda x: x.text, li.find_next_siblings()
                            ))

            """
            all episode list:
            eps: [id, date]
            """
            if (eps := s.find(class_='episodelist')):
                if (li := eps.find_all('li')):
                    d['episode'] = list(map(
                        lambda x: {
                            x[0].__str__(): self.get_id(
                                x[1].a.attrs.get('href')),
                            'date': x[1].span.find_next_sibling().text
                        }, enumerate(li, 1)
                    ))
                else:
                    d['episode'] = {}
            return d
        return {}

    """
    get all download, and stream url
    """
    async def get_download_list(self, eps: str, exinfo: bool = False) -> Union[Dict[str, Sequence[Collection[str]]], None]:
        page = await self.get(f"/{eps}/")
        soup = self.parse(page.text)
        d = {}
        if (box := soup.find(class_="boxdownload")):
            """
            @downloadLink: list all server/eps download
            """
            d['id'] = eps
            d['link'] = list(map(
                lambda x: {
                    x.find(class_='name').text: list(map(
                        lambda x: {
                            x.text: x.attrs.get('href')
                        }, x.find_all('a')
                    ))
                }, box.find_all(
                    class_='liner')
            ))

            """
            @thumbnail: search last quality (best),
            with regex ,set empty str if can't find it
            """
            if (img := re.search(r"srcset\=\"(?P<url>[^\"]+?)\"", page.text)):
                d['thumbnail'] = img.groupdict().get('url').split(
                    ", ")[0].split()[0]
            else:
                d['thumbnail'] = ''

            """
            @stream: list stream url, set empty list if can't find it.
            """
            if (openstream := soup.find_all('div', class_='openstream')):
                d['stream'] = list(map(
                    lambda x: {
                        f"stream{x[0]}": x[1].iframe.attrs.get('src')},
                    enumerate(openstream, 1)
                ))
            else:
                d['stream'] = []

            if exinfo:
                """
                extended info from download page for jav.
                """
                if (contentpost := soup.find(class_='contentpost')):
                    trim_unicode = lambda r: re.sub(r'[^\x00-\x7F]+', '', r).strip()
                    search_size = lambda s: re.findall(r'\b(\d+P)\s*:\s*([^|\s]+)',s)
                    if (string := re.findall(r'\b([^:\n]+)\s*:\s*([^\n]+)', contentpost.text)):
                        for i, v in dict(string).items():
                            """
                            handle no key 'size'. e.g: 360P : 313mb   |   480P : 386mb.
                            as {"360P": "313mb   |   480P : 386mb"}
                            """
                            if  re.match(r"\b\d{1,4}P", i):
                                i = trim_unicode("{} : {}".format(
                                    i, v
                                ))
                                if (data_size := search_size(i)):
                                    d['size'] = dict(data_size)
                                    continue
                                else:
                                    continue
                            """
                            string size to dict: {"Size": "360P : 533mb |\u00a0 \u00a0480P : 799mb"}
                            as {"Size": "360P":"533mb", "480P":"799mb"}. leave if not the size
                            """
                            if (data_size := search_size(v.strip())):
                                d[i.strip()] = dict(data_size)
                            else:
                                d[i.strip()] = v.strip()
            return d
        return None
    
    """
    get genre list: [unused, separated call]
    """
    async def get_genre_list(self) -> Union[Dict[str, str], None]:
        page = await self.get(f"/genre-list/")
        soup = self.parse(page.text)
        if (genre := soup.find('div', class_='genres')):
            return {
                _.a.text.strip(): self.get_id(
                    _.a.attrs.get('href')
                ) for\
                    _ in genre.find_all('li')
            }
        return None
