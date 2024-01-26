#!/usr/bin/python
# @github.com/motebaya - 20.01.2024
# no asynchronous anymore :<
import os
from app.models.nekogit import Nekogit
from app.models.helpers.Utils import Util
from app.models.database.Migration import TableManager
from argparse import ArgumentParser, RawTextHelpFormatter

class Manage:
    logger = None
    
    @staticmethod
    def goDatabase() -> None:
        sql = TableManager()
        dbgenrepath = Util.getdbpath('hanime/Json/genre-list.json')
        if Util.path_exist(dbgenrepath):
            for genre in (Util.loadfile(dbgenrepath, 'dict')).items():
                sql.setGenres(*genre)
        else:
            Util.log(f"[red]You don't have a json database genre list in[reset] -> [yellow]{dbgenrepath}![reset]")
        dbpath = Util.getdbpath('hanime/Json/hanime-list.json')
        if Util.path_exist(dbpath):
            db = Util.loadfile(dbpath, 'dict')
            for index, item in enumerate(db, 1):
                Util.log(f"[green][>][reset] Process -> {index}/{len(db)} items..")
                episode = item.pop("episode")
                sql.setHanime(item)
                for num, eps in enumerate(episode, 1):
                    Util.log(f"[green][>][reset] Process -> {index}/{len(db)} Episodes..")
                    sql.setEpisode(
                        item.get("id"),
                        eps.get('date', '-'),
                        eps[str(num)]
                    )
        else:
            Util.log(f"[red]You don't have a json database genre list in[reset] -> [yellow]{dbpath}![reset]")
        sql.connect.commit()
        sql.connect.close()
        Util.log(f"Ok, done. sqlite3 dbpath -> {sql.dbname.replace(os.getcwd(), '')}")
        return

    @staticmethod
    def goExtract(_type: str, verbose: bool) -> None:
        neko = Nekogit(verbose)
        for log in (Manage, Util):
            if not getattr(log, "logger"):
                log.logger = neko.logger

        match _type.lower():
            case "hanime-index":
                if (hanime_index := neko.get_hanime_index()):
                    Util.saveto(
                        hanime_index,
                        Util.getdbpath(
                            "hanime/Json/hanime-index.json"
                        )   
                    )
                return
            case "hanime-list":
                neko.get_hanime_list()
                if (len(neko.hanime_results) != 0):
                    Util.saveto(
                        neko.hanime_results,
                        Util.getdbpath(
                            "hanime/Json/hanime-list.json"
                        )
                    )
                return
            case "cover":
                return neko.get_covers_list()
            case "thumbnail":
                return neko.get_thumbnails_list()
            case "genre":
                if  (genres := neko.get_genre_list()):
                    Util.show_info(genres, "genres list")
                    Util.saveto(
                        genres,
                        Util.getdbpath(
                            "hanime/Json/genre-list.json"
                        )
                    )
                return

if __name__=="__main__":
    parser = ArgumentParser(
        description="\n\tNekogitv2 CLI \n   Author: @github.com/motebaya\n\n A CLI tool used to manage data such as databases, images, and others",
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("-e", "--extract", help="extract: thumnbnail, cover, hanime index/list from site",
        choices=['hanime-list', 'hanime-index', 'cover', 'thumbnail', 'genre'], metavar="")
    parser.add_argument(
        "-m",
        "--migrate",
        dest="migrate",
        help="migrate a json database genre/hanime list to sqlite3 database.",
        action="store_true"
    )
    group = parser.add_argument_group("Optional")
    group.add_argument("-V", "--verbose", action="store_true", help="enable debug mode")
    args = parser.parse_args()
    if (args.extract):
        print(parser.description, end="\n\n")
        try:
            Manage.goExtract(args.extract, args.verbose)
        except (KeyboardInterrupt):
            Util.log("[red]Stopped manually[reset]")
    elif args.migrate:
        print(parser.description, end="\n\n")
        Manage.goDatabase()
    else:
        parser.print_help()