#!/usr/bin/env python3
# author: @github.com/motebaya
# Copyright 2023.06.3
# file: __main__

from nekopoiv2 import (
    extract_link,
    extract_site,
    extract_images,
    logger,
    asyncio,
    re,
    os
)

from argparse import (
    ArgumentParser,
    RawTextHelpFormatter,
    FileType
)

if __name__ == "__main__":
    parser = ArgumentParser(
        description="\t Poi Poi Nekopoi\n [ scrapper and image downloader]\n        @github.com/motebaya", formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-s", "--site", help="extract all hentai by site host: [rajahentai.xyz, nekopoi.care]", metavar="", type=str)
    parser.add_argument(
        "-b", "--bypass", help="bypass redirect/shortlink url: [bokepku.xyz, ouo.io] from *arg [file]", type=FileType('r'), metavar="")
    parser.add_argument(
        "-i", "--image", help="fetch and download all cover/thumbnail image from *arg [file]", metavar="", type=str)
    args = parser.parse_args()
    try:
        if args.site:
            if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', args.site):
                asyncio.run(
                    extract_site(
                        args.site
                    )
                )
            else:
                logger.warning('wrong site type!')
        elif args.bypass:
            asyncio.run(
                extract_link(
                    args.bypass.read()
                )
            )
        elif args.image:
            if os.path.exists(args.image):
                asyncio.run(
                    extract_images(
                        args.image
                    )
                )
            else:
                logger.warning(f"file: {args.image} not found.")
        else:
            parser.print_help()
    except (KeyboardInterrupt):
        logger.warning("stopped manually.")
