#!/usr/bin/env python3
# author: @github.com/motebaya
# Copyright 2023.06.7 
# file: nekopoiv2.py

import ssl, asyncio, re, aiofiles, time
from aiohttp import ClientSession
from rich.prompt import Prompt
from typing import Dict
from time import sleep as delay

from lib import (
    Nekopoi,
    Console,
    logging,
    Panel,
    logger,
    os
)

from rich.progress import (
    Progress, 
    SpinnerColumn, 
    BarColumn, 
    TextColumn, 
    DownloadColumn, 
    TransferSpeedColumn, 
    TimeRemainingColumn
)

class Extractor(object):
    """
    separate class not as child.
    """
    def __init__(self) -> None:
        self.module = Nekopoi.Nekopoi()
        self.result = {'jav_list': [], 'hentai_list':[]}
        self.console = Console(highlight=False)
    
    async def extract_site(self, pagetype: str) -> None:
        """
        extract all list from hentai/jav page.

        Args:
            pagetype (str): (hentai/jav)-list
        Optional:
            - add delay 1-5 second each async http request to avoid exception: ssl.SSLWantReadError.
            - stop manually, every: [optional] e.g: 100. then continue again.
        """
        if self.module.dbNotEmpty():
            self.module.show_message("[green] DB exists -> {}".format(self.module.db_path))
            self.result = self.module.load_db()
        
        """
        fetch genre list if result.init still don't have genre_list after load from old db.
        """
        if 'genre_list' not in self.result:
            self.module.show_message("[green] getting genre list..[white]")
            if (genre_list := await self.module.get_genre_list()):
                self.result['genre_list'] = genre_list

        try:
            old_tittle_list = []
            title_list = list(filter(None, [
                _ async for _ in self.module.get_title_list(
                    pagetype
                )
            ]))

            """
            IF auto load = if old data length less than new data length from title list.
            """
            dblength = len(self.result.get("{}_list".format(pagetype)))
            if dblength != 0 and dblength <= len(title_list):
                old_tittle_list = list(map(
                    lambda t: t.get('title', '').lower(),
                    self.result.get("{}_list".format(pagetype))
                ))
                self.module.show_message("[white] found, old db with:: [yellow]{} items[white] and new db with [yellow]{} items[white]".format(dblength, len(title_list)))
                ask = Prompt.ask(f"[white] Continue from index [cyan]:: {dblength}? [y/n]:")
                if (ask.lower() == 'y'):
                    title_list = title_list[dblength:]

            # start execute extract.
            logger.info("Getting total item: {}".format(
                str(len(title_list))
            ))

            for i, j in enumerate(title_list, 1):
                # old items is exist and new item title in old items, then skip it.
                if all([j.get('title', '').lower() in old_tittle_list, bool(old_tittle_list)]):
                    self.result[f"{pagetype}_list"][
                        old_tittle_list.index(
                            j.get('title', '').lower()
                        )
                    ].update(j)
                    self.module.show_message("[red] Skipping [cyan]:: [yellow]{}[white]".format(
                        j.get('title', '')
                    ))
                    continue

                self.module.show_message("[white] Process :: [cyan]{}[white] of [yellow]{}[white]".format(
                    i, str(len(title_list))
                ))
                match pagetype:
                    case "hentai":
                        self.module.show_message("[white] getting info [cyan]:: [green] {} [white]".format(
                            j.get('id')
                        ))
                        if (info := await self.module.get_hentai_info(j.get('id'))):
                            info.update(j)
                            if info.get('episode'):
                                episode = info.pop('episode')
                                self.module.show_info(info, j.get('title'))

                                # fetch each episode.
                                for num, ep in enumerate(episode, 1):
                                    self.module.show_message("[white] getting download list [cyan]:: [green]{}[white]".format(
                                        ep[str(num)]
                                    ))
                                    if (eps := await self.module.get_download_list(ep[str(num)])):
                                        episode[num-1][str(num)] = eps
                                        info['episode'] = episode
                                    else:
                                        self.module.show_message("[red] skip :: [white]{}".format(
                                            ep[str(num)]
                                        ))
                            else:
                                """
                                idk, why some of new hentai don't have episode list.
                                maybe admin forgot to add it?
                                """
                                self.module.show_message(
                                    "[red] skipping get episode [cyan]:: [yellow]{}[white]".format(
                                        j.get('title')
                                    )
                                )
                            self.result['hentai_list'].append(
                                info
                            )
                        else:
                            self.module.show_message("[red] Failed get info :: [white]{}".format(
                                j.get('id')
                            ))
                    case "jav":
                        """
                        jav is movie and don't have episodes list like hentai.
                        """
                        self.show_message("getting [yellow]JAV [cyan]:: [green]{}".format(
                            j.get('id')
                        ))
                        if (episode := await self.module.get_download_list(j.get('id'), True)):
                            self.module.show_info({
                                i: x for i, x in episode.items() if i not in ['id', 'stream', 'link', 'thumbnail']
                            }, j.get('title'))
                            j.update(episode)
                            self.result['jav_list'].append(j)
                        else:
                            self.module.show_message("[red] skipping [cyan]:: [white]{}".format(
                                j.get('id')
                            ))
                time.sleep(0.5)
            # all completed, then save it.
            self.module.savedata(self.result)
        except (asyncio.CancelledError, ssl.SSLWantReadError, KeyboardInterrupt) as e:
            """
            manually stop: trigger CTRL + C -> save current result.
            """
            logger.warning("Exception: stopped manually. saving data..")
            if self.result['hentai_list'] or self.result['jav_list']:
                self.module.savedata(self.result)
            return
    
    async def extract_images(self, dataType: str) -> None:
        """
        - download all minimum image quality cover and thumbnail.
        - image path -> (hentai/(cover/thumbnail) / (jav)/thumbnail)
        Args:
            dataType (str): which data?
        """
        # load and die if nothing.
        if self.module.dbNotEmpty():
            db = self.module.load_db()
        else:
            self.module("You don't have any database!")
            exit(1)

        url = lambda x: re.match('^https?\:\/\/.+$',x)
        selected_data = db['hentai_list' if dataType.lower() == 'hentai' else 'jav_list']
        for num, image in enumerate(selected_data, 1):
            try:
                self.module.show_message("[white]Process [cyan]:: [green]{}[white] of [yellow]{} [white]".format(
                    num, len(selected_data)
                ))
                match dataType:
                    case 'hentai':
                        # cover
                        if url(image.get('image', '')):
                            filename = await self._download_content(
                                image.get('image'),
                                'hentai/cover'
                            )
                            db['hentai_list'][num-1]['image'] = filename
                        else:
                            self.module.show_message(
                                "[red]Skipping: [yellow]{} non url str[white]".format(
                                    image.get("image")
                            ))

                        # fetch each thumbnail from episodes.
                        for x, thumbnail  in enumerate(image['episode']):
                            if url(thumbnail[str(x+1)].get('thumbnail', '')):
                                self.module.show_message("downloading thumbnail[cyan] :: [green]{} of [yellow]{}".format(
                                    x+1, len(thumbnail[str(x+1)])-1
                                ))
                                filename = await self._download_content(
                                    thumbnail[str(x+1)].get('thumbnail'),
                                    'hentai/thumbnail'
                                )
                                db['hentai_list'][num-1]['episode'][x][str(x + 1)]['thumbnail'] = filename
                            else:
                                self.module.show_message(
                                    "[red]Skipping: [yellow]{} non url str[white]".format(
                                        thumbnail[str(x + 1)].get('thumbnail')
                                    ))
                    case 'jav':
                        # jav images
                        if url(image.get('thumbnail', '')):
                            self.module.show_message(
                                "downloading:: [yellow]JAV [white] thumbnail[cyan]{} [white]of [cyan] {}[white]".format(
                                    num, len(db)
                            ))
                            filename = await self._download_content(
                                image.get('thumbnail'),
                                'jav/thumbnail'
                            )
                            db['jav_list'][num-1]['thumbnail'] = filename
                        else:
                            self.module.show_message(
                                "[red]skip :: [yellow]{}, [white]not url!.".format(
                                    image.get('thumbnail')
                                )
                            )
            except (asyncio.CancelledError, KeyboardInterrupt, ssl.SSLWantReadError):
                logger.warning("Exception: stopped manually. saving data..")
                delay(1)
                self.module.savedata(db)
                return
        logger.info("Completed: saving data...")
        delay(1)
        self.module.savedata(db)

    async def _download_content(self, url: str, itype: str) -> None:
        """
        rich progress bar downloader.

        Args:
            - url (str): image url.
            - itype (str): type image cover/thumbnail.
        """
        filename = os.path.realpath("./database/{}/{}".format(
            itype, url.split('/')[-1]
        )) # default filename for image path
        async with ClientSession(headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }) as session:
            if not os.path.exists(filename):
                async with session.get(url) as response:
                    async with aiofiles.open(filename, "wb") as f:
                        with Progress(
                            SpinnerColumn(speed=1.5),
                            TextColumn("[green] Downloading..", justify="right"),
                            BarColumn(),
                            "[progress.percentage]{task.percentage:>3.0f}%",
                            DownloadColumn(
                                binary_units=False
                            ),
                            TransferSpeedColumn(),
                            TimeRemainingColumn(),
                            console=Console(),
                            transient=True
                        ) as progress:
                            task = progress.add_task(
                                "[green] Downloading..", total=int(response.headers.get('content-length', 0))
                            )
                            async for content in response.content.iter_chunks():
                                await f.write(
                                    content[0]
                                )
                                progress.update(
                                    task, advance=len(content[0])
                                )
                            await f.close()
                            progress.stop()
                    self.module.show_message(f"[green]Completed..saved as: [blue]{os.path.basename(filename)}")
            else:
                self.module.show_message(f"[red]skipping.. [blue]{os.path.basename(filename)} [green] file exist!")
        return os.path.basename(filename)
