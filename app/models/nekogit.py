#!/usr/bin/env python3
# github.com/motebaya - 21.01.2023
# module handler
# file: app/models/nekogit.py

from app.models.helpers.Utils import Util
from app.models.lib.Nekopoi import Nekopoi
from typing import List, Any, Dict
from rich.prompt import Prompt
from httpx import ConnectError, ReadTimeout as httpxReadTimeout
from httpcore import ReadTimeout
import re, random, time

class Nekogit(Nekopoi):
    def __init__(self, verbose: bool) -> None:
        super().__init__(verbose)
        self.hanime_results: List[Any] = []
        self.isurl = lambda url: re.match('^https?\:\/\/.+$',url)
    
    def add_random_name(self, suffixname: str) -> str:
        return "{}-{}".format(
            str(random.randint(1024, 10240)),
            suffixname
        )

    def get_hanime_index(self) -> List[Dict[str, Any]] | None:
        """
        -> get all ordered hanime list from index page.
        """
        try:
            if (hanimeindex := self.getHentaiList()):
                self.logger.info(f"Fetching, {len(hanimeindex)} Hanime index list..")
                return hanimeindex
            self.logger.error(" Failed get hanime index list..!")
            return
        except Exception as e:
            self.logger.error(f"Exception::[red]{str(e)}")
            return

    def get_hanime_list(self) -> None:
        """
        -> get all hanime info from hanime index.
        -> stop/continue anytime.
        """
        try:
            indexlist = Util.getdbpath("hanime/Json/hanime-index.json")
            indexlist = Util.loadfile(indexlist, 'dict') if Util.path_exist(indexlist) \
                else self.get_hanime_index()

            olddbpath = Util.getdbpath("hanime/Json/hanime-list.json")
            if Util.path_exist(olddbpath):
                self.hanime_results = Util.loadfile(olddbpath, 'dict')
                Util.log(f"[red][!][reset] database exist with length: [green]{len(self.hanime_results)}[reset] and current length: [yellow]{len(indexlist)}[reset]")
                if (Prompt.ask(
                    f" [yellow][?][white] Continue from index -> {len(self.hanime_results)}?:", 
                    choices=['y','n'], default="y"
                ).lower() == "y"):
                    indexlist = indexlist[len(self.hanime_results):]
                else:
                    self.logger.warning("Aborted")
                    exit(0)

            # start scrape
            for i, items in enumerate(indexlist, 1):
                Util.log("[>] Process items -> ([green]{}[reset]/[yellow]{}[reset])".format(i, len(indexlist)))
                Util.log("[>] Getting info -> [yellow]{}[reset]".format(items.get("title")))
                if (info := self.getHentaiInfo(items.get("id"))):
                    info.update(items)
                    if (info.get('eps')):
                        episode = info.pop('eps')
                        Util.show_info(info, info.get("title"))
                        for e, eps in enumerate(episode, 1):
                            Util.log(f"[>] Getting download list -> [yellow]{eps[str(e)]}[reset] - [[green]{e}[reset]/[yellow]{len(episode)}[reset]]")
                            if (download_list := self.getDownloadList(eps[str(e)])):
                                episode[e-1][str(e)] = download_list
                                info['episode'] = episode
                            else:
                                Util.log(f"[!] Couldn't get download list from -> [yellow]{eps[str[e]]}[reset]")
                                continue
                    else:
                        Util.log(f"[!] Couldn't get episode list from -> [yellow]{info.get('title')}[reset], maybe it's teaser/PV")
                        continue
                    self.hanime_results.append(info)
                else:
                    Util.log("[!] Couldn't get info from title -> [yellow]{info.get('title')}[reset]")
                    continue
            Util.log(f"complete getting info [green]{len(self.hanime_results)}[reset] hanime list..!")
            return
        except (KeyboardInterrupt) as e:
            Util.log(f"Exceptions::[red]SIGINT[reset], stopped!")
            return 
    
    def get_covers_list(self) -> None:
        """
        -> fetch and download all images covers.
        """
        dbpath = Util.getdbpath("hanime/Json/hanime-list.json")
        if not Util.path_exist(dbpath):
            self.logger.error("Error: you don't have a json database hanime list.")
            return
        
        skipped = []
        downloaded = 0
        db = Util.loadfile(dbpath, "dict")
        try:
            get_suffixname = lambda item: item.get("image").split("/")[-1]
            for index, item in enumerate(db):
                Util.log("[>] Process items -> ([green]{}[reset]/[yellow]{}[reset])".format(index+1, len(db)))
                if self.isurl(item.get("image")):
                    suffixname = get_suffixname(item)
                    if suffixname in skipped:
                        suffixname = self.add_random_name(suffixname)
                    fname, isexist = Util.download(
                        item.get("image"), Util.getdbpath(
                            "hanime/covers/{}".format(
                                suffixname
                            )
                        )
                    )
                    downloaded +=1 
                    if isexist:
                        skipped.append(fname)
                    Util.log(f"[%] Changed images url to [yellow]{fname}[reset]")
                    db[index]['image'] = fname
                else:
                    skipped.append(get_suffixname(item))
                    Util.log(f"[!] [red]skipped, [yellow]{get_suffixname(item)}[reset] is not url str...!")
                    continue
            self.logger.info(f"completed downloading [green]{downloaded}[reset] images covers.")
            Util.saveto(db, dbpath)
            return
        except (ConnectionResetError, ConnectError, TimeoutError, ReadTimeout, httpxReadTimeout) as e:
            self.logger.error(f"Exception:{str(e)}, stopped. try again!")
            return
    
    def get_thumbnails_list(self) -> None:
        """download all thumbnails of each episode"""
        dbpath = Util.getdbpath("hanime/Json/hanime-list.json")
        if not Util.path_exist(dbpath):
            self.logger.error("Error: you don't have a json database hanime list.")
            return
        
        skipped = []
        downloaded = 0
        db = Util.loadfile(dbpath, 'dict')
        try:
            for index, item in enumerate(db):
                Util.log("[>] Process items -> ([green]{}[reset]/[yellow]{}[reset])".format(index+1, len(db)))
                for num, eps in enumerate(item.get("episode", []), 1):
                    Util.log("[>] Process Thumbnails -> ([green]{}[reset]/[yellow]{}[reset])".format(num, len(item.get('episode',[]))))
                    thumbnail = eps[str(num)].get("thumbnail")
                    if self.isurl(thumbnail):
                        suffixname = thumbnail.split("/")[-1]
                        if suffixname in skipped:
                            suffixname = self.add_random_name(suffixname)
                        fname, isexist = Util.download(
                            thumbnail, Util.getdbpath(
                                "hanime/thumbnails/{}".format(
                                    suffixname
                                )
                            )
                        )
                        downloaded +=1
                        if isexist: 
                            skipped.append(fname)

                        Util.log(f"[<] Thumbnail changed: [yellow]{fname}[reset].")
                        db[index]['episode'][num-1][str(num)]['thumbnail'] = fname
                        time.sleep(0.5)
                    else:
                        skipped.append(thumbnail)
                        Util.log(f"[!] [red]skipped, [yellow]{thumbnail}[reset] is not url str...!")
                        continue
            self.logger.info(f"completed downloading [green]{downloaded}[reset] images thumbnails.")
            Util.saveto(db, dbpath)
            return
        except (ConnectionResetError, ConnectError, TimeoutError, ReadTimeout, httpxReadTimeout) as e:
            self.logger.error(f"Exception:{str(e)}, stopped. try again!")
            return

    def get_genre_list(self) -> None:
        """get genre list"""
        Util.log("getting genre list..")
        try:
            return self.getGenreList()
        except Exception as e:
            Util.log(f"Exception::{str(e)}")
            return
            
                    
            
            

            