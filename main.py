#!/usr/bin/env python3
# author: @github.com/motebaya
# Copyright 2023.06.3 
# file: __main__

from nekopoiv2 import asyncio, Extractor
from argparse import (
    ArgumentParser,
    RawTextHelpFormatter
)
from CreateDb import (
    Create_db,
    logging,
    logger
)

if __name__=="__main__":
    parser = ArgumentParser(description="\t Poi Poi Nekopoi\n  [ nekopoi.care site extractor/mirror ]\n      @github.com/motebaya", formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-d", "--database", help="create sqlite3 db from json database",
        type=str, choices=['hentai', 'jav'], metavar=''
    )
    parser.add_argument(
        "-e", "--extract", help="extract all content from page hentai/Jav list",
        type=str, choices=['hentai', 'jav'], metavar=""
    )
    parser.add_argument(
        "-i", "--image", help="fetch and download all cover/thumbnail images,\n*args[3d-hentai, hentai, jav]",
        metavar="", type=str, choices=['hentai', 'jav']
    )
    group = parser.add_argument_group("Optional")
    group.add_argument(
        "-V", "--verbose", help="enable debug logging mode", action="store_true"
    )
    extractor = Extractor()
    args = parser.parse_args()
    if not args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    try:
        if args.extract:
            logger.info(f"extracting page for {args.extract}")
            asyncio.run(extractor.extract_site(
                args.extract
            ))
        elif args.image:
            logger.info(f"extracting images for {args.image}.")
            asyncio.run(extractor.extract_images(
                args.image
            ))
        elif args.database:
            create = Create_db(args.database)
            dbjson = create.readAsJson()
            
            # set genre for hentai
            if args.database == 'hentai':
                for g in dbjson.get('genre_list').items():
                    create.set_genre(*g)

            # set all list of hentai
            selected_db = dbjson.get("{}_list".format(args.database))
            for x, y in enumerate(selected_db):
                logger.info(
                    "queries :: set_{} -> {} of {}".format(
                        args.database, str(x + 1), len(selected_db)
                ))
                match args.database:
                    case 'hentai':
                        episod_data = y.pop('episode')
                        create.set_hentai(y)
                
                        # set each episodes row.
                        for num, episod in enumerate(episod_data, 1):
                            logger.info(f"queries :: set_episode : {num} of {len(episod_data)}")
                            create.set_episode(
                                y.get('id'),
                                episod[str(num)],
                                episod.get('date')
                            )
                    case 'jav':
                        create.set_jav(y)
            create.create_visitorTable()
            create.connect.commit()
            create.connect.close()
        else:
            parser.print_help()
    except (KeyboardInterrupt):
        logger.warning("stopped manually.")
