#!/usr/bin/python3
# @github.com/motebaya - 20.01.2024
# main module
# file: app/models/lib/Nekopoi.py

from . import Init
from typing import List, Dict, Any
import re

class Nekopoi(Init):
    
    def __init__(self, verbose: bool) -> None:
        super().__init__(verbose)
        self.client = self.createSession(host="https://nekopoi.care")
    
    def getHentaiList(self) -> List[Any] | None:
        """-> get index ordered hanime list.

        :return List[Any] | None: result
        """
        page = self.client.get("/hentai-list/", timeout=10)
        if (hentai_list := self.parse(page).find_all(class_='title-cell')):
            return list(map(lambda item: {
                "title": item.a.text,
                "id": self.get_id(
                    item.a.get("href")
                )
            }, hentai_list))
        return None
    
    def getHentaiInfo(self, hanimeid: str) -> Dict[str, Any] | dict:
        """-> get hanime info by id.
        -> thumbnail/cover -> info & genre -> eps list

        :param str hanimeid: hanime id from index.
        :return Dict[str, Any] | dict: result
        """        
        soup = self.parse(self.client.get(f"/hentai/{hanimeid}/"))
        d: Dict[str, Any] = {}
        if (s := soup.find(class_='animeinfos')):
            if (desc := s.find(class_="imgdesc")):
                d.update({
                    "image": desc.img.get('src'),
                    "desc": ''.join(map(
                        lambda x: x.text,
                        desc.find_all('p')
                    ))
                })
            if (info := s.find(class_='listinfo')):
                for li in map(lambda x: x.find('b'), info.find_all('li')):
                    if li:
                        k: str = re.sub(r"^\:\s+", "", li.next_sibling.strip())
                        if not k.startswith(':'):
                            d[li.text] = k
                        else:
                            d[li.text] = ", ".join(map(
                                lambda x: x.text, li.find_next_siblings()
                            ))
            # eps list: [index -> id, date -> str date]
            if (eps := s.find(class_='episodelist')):
                d['eps'] = list(map(lambda x: {
                    x[0].__str__(): self.get_id(
                        x[1].a.attrs.get('href')),
                    'date': x[1].span.find_next_sibling().text
                    }, enumerate(eps.find_all("li"), 1)
                )) or {}
            return d
        return {}
    
    def getDownloadList(self, eps: str) -> Dict[str, Any] | None:
        """-> get server & quality download/stream list url.

        :param str eps: episode id
        :return Dict[str, Any] | None: result
        """        
        page = self.client.get(f"/{eps}/").text
        soup = self.parse(page)
        d: Dict[str, Any] = {}
        if (box := soup.find(class_="boxdownload")):
            d.update({
                "id": eps,
                "link": list(map(lambda x: {
                    x.find(class_='name').text: list(map(
                        lambda x: {
                            x.text: x.attrs.get('href')
                        }, x.find_all('a')
                    ))
                }, box.find_all(
                    class_='liner')
                ))
            })

            if (img := re.search(r"srcset\=\"(?P<url>[^\"]+?)\"", page)):  
                d['thumbnail'] = img.groupdict().get('url').split(
                    ", ")[0].split()[0]
            else:
                d['thumbnail'] = ''

            if (openstream := soup.find_all('div', class_='openstream')):
                d['stream'] = list(map(
                    lambda x: {
                        f"stream{x[0]}": x[1].iframe.attrs.get('src')},
                    enumerate(openstream, 1)
                ))
            else:
                d['stream'] = []
            return d
        return None
    
    def getGenreList(self) -> Dict[str, str] | None:
        """get genre list.

        :return Union[Dict[str, str], None]: result.
        """
        soup = self.parse(self.client.get(f"/genre-list/").text)
        if (genre := soup.find('div', class_='genres')):
            return {
                _.a.text.strip(): self.get_id(
                    _.a.attrs.get('href')
                ) for\
                    _ in genre.find_all('li')
            }
        return None
