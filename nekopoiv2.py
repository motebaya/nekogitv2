#!/usr/bin/env python3
# author: @github.com/motebaya
# Copyright 2023.06.7 
# file: nekopoiv2.py

import ssl, asyncio, re, aiofiles
from aiohttp import ClientSession
from tqdm import tqdm
from lib import (
    Nekopoi,
    Rajahentai,
    urlparse,
    logger,
    json,
    os
)

async def download(**kwargs: dict) -> str:
    """
    source: https://github.com/motebaya/MMManga/blob/main/lib/__init__.py#L127
            https://stackoverflow.com/questions/35388332/how-to-download-images-with-aiohttp
    fetch all image list with async, skip for update (reuse) if image already downloaded
    """
    async with ClientSession() as session:
        async with session.get(kwargs.get('u')) as response:
            filename = os.path.realpath("./src/{}/{}".format(
                kwargs.get("t"),
                kwargs.get('u').split('/')[-1]
            ))
            if not os.path.exists(filename):
                logger.debug(f"downloading: {os.path.basename(filename)}")
                async with aiofiles.open(filename, mode="wb") as f:
                    t = tqdm(
                        asyncio.as_completed(session),
                        total=int(response.headers.get("content-length", 0)), unit="B", unit_scale=True
                    )
                    async for content in response.content.iter_chunks():
                        await f.write(content[0])
                        t.update(
                            len(content[0])
                        )
                    await f.close()
                    t.close()
                return os.path.basename(
                    filename
                )
            logger.info(f"Skip Download: {filename} already exist!")
            return os.path.basename(
                filename
            )

async def extract_images(fileData: str) -> None:
    """
    download all minimum resolution image cover and thumbnail
    it will saved to /src/cover\/thumbnail
    REUSE: for update auto skip if non url image str
    """
    data = json.loads(
        open(fileData).read()
    )
    l = len(data)
    is_url = (lambda x: \
        re.match('^https?\:\/\/.+$',x)
    )
    try:
        # fetch cover
        for j, k in enumerate(data):
            if is_url(k.get('image', '')):
                logger.debug(f"downloading cover: ({j+1}) of ({len(data)})")
                filename = await download(
                    u=k.get('image'),
                    t="cover"
                )
                l -= 1

                data[j]['image'] = filename
                # thumbnail
                for x, y in enumerate(k['episode']):
                    if is_url(y[str(x + 1)].get('thumbnail', '')):
                        logger.debug(f"downloading thumbnail: ({x + 1}) of ({len(k['episode'])})")
                        filename = await download(
                            u=y[str(x + 1)].get('thumbnail'),
                            t="thumbnail"
                        )
                        data[j]['episode'][x][str(x + 1)]['thumbnail'] = filename
                    else:
                        logger.info(
                            "Skipping: {} non url str".format(
                                y[str(x + 1)].get('thumbnail')
                            ))
            else:
                logger.info(
                    "Skipping: {} non url str".format(
                        y[str(x + 1)].get('thumbnail')
                ))
        Nekopoi.Nekopoi().savedata(
            os.path.basename(
                fileData
            ), data
        )
    except (asyncio.CancelledError, KeyboardInterrupt):
        if l != len(data):
            logger.warning(f"Exception, from last index: \033[33m{str(len(data) - l)}")
            Nekopoi.Nekopoi().savedata(
                ".cache-{}-{}".format(
                    str(len(data) - l),
                    os.path.basename(
                        fileData
                    )
                ), data
            )
        else:
            logger.warning("Exception, nothing data to save")

async def extract_site(site: str) -> None:
    """
    extract all hentai list from site
    @debug on
    """
    result = [] # store dict to here
    if site in ['rajahentai.xyz', 'nekopoi.care']:
        sitetitle = site.split(".")[0].title()
        dbname = "{}-hentai-list.json".format(
            sitetitle
        )
        module = eval("{}.{}()".format(
            sitetitle, sitetitle
        ))

        try:
            hentai_list = [
                _ async for _ in module.get_hentai_list()
            ]
            if len(hentai_list) != 0:
                logger.debug(f"item collected: {len(hentai_list)}")
                for j, k in enumerate(filter(None, hentai_list)):
                    logger.debug(f"({j+1} of {len(hentai_list)}) getting info: {k.get('title')}")

                    # get hentai info
                    data = await module.get_hentai_info(
                        k.get('id')
                    )
                    data.update(k)

                    if not data['Episode'].strip():
                        data['Episode'] = len(data['episode'])
                    # display info as debug
                    module.showinfo(data)
                    for i, e in enumerate(data['episode'], 1):
                        logger.debug(f"getting all {len(data.get('episode'))} eps..")
                        episodes = await module.get_download_list(
                            e[str(i)]
                        )
                        if episodes:
                            logger.debug(f"total quality get: {len(episodes)}")
                            data['episode'][i-1][str(i)] = episodes
                        else:
                            logger.warning(f"failed get eps: {str(i)}")

                    result.append(data)
                module.savedata(dbname, result)
                return
            else:
                logger.warning(f"failed get hentai list of: {site}")
                return
        except (
            asyncio.CancelledError, ssl.SSLWantReadError, KeyboardInterrupt, AttributeError
        ) as e:
            if len(result) != 0:
                """
                save cache, if encountered some error, using array slice to continue
                from last line, e.g: hentai_list[lastline:]
                """
                cachename = f'.cache-{site}-{len(result)}.json'
                with open(cachename, 'w') as f:
                    f.write(
                        json.dumps(
                            result
                        )
                    )
                logger.warning(f"Exception with: {str(e)}, cache saved as: {cachename}")
                return
            else:
                logger.warning("Exception, no cache to save!")
                return
    else:
        logger.warning(f"invalid site: {site}")

async def extract_link(data: str) -> None:
    """
    extract/bypas all shortlink url from site
    [bokepku.xyz, ouo.io]
    """
    prog = {
        'bokepku': Rajahentai.Rajahentai(),
        'ouo': Nekopoi.Nekopoi()
    }

    _regex = re.compile(
        r"https?:\/\/(?:ouo\.io\/[\w+]*|bokepku.xyz\/\w+\.php\?id\=[0-9]+)")

    if (url_list := _regex.findall(data)):
        tipe = urlparse(
            url_list[0]
        ).netloc.split(
            ".")[0]

        failed_get = len(url_list)
        logger.debug(f"detected: {tipe}, total url collected: \033[32m{len(url_list)}")
        try:
            for j, k in enumerate(url_list, 1):
                logger.debug(f" ({j}) of ({len(url_list)}) getting redirect url: {k}")
                final_url = await prog[tipe].get_redirect(k)
                if final_url:
                    logger.info(f"bypassed: {final_url}")
                    data = data.replace(
                        k, final_url
                    )
                    failed_get -= 1
                else:
                    continue
        except (KeyboardInterrupt, asyncio.CancelledError):
            if failed_get != len(url_list):
                """
                save last bypassed index
                """
                prog[tipe].savedata(
                    "{}-hentai-list.json".format(
                        prog[tipe].__class__.__name__.title()
                    ),
                    data
                )
                logger.info("Exception, data saved with last line: {}".format(
                    str(len(url_list) - failed_get)
                ))
                return
            else:
                logger.warning("Exception, no data to saved")
                return
    return
