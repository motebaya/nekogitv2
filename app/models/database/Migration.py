#!/usr/bin/python3
# github.com/motebaya - 23.01.2023
# raw json migration to sqlite3 db
# file: app/models/database/Migration.py

import os, sqlite3, json
from rich.prompt import Prompt
from app.models.helpers.Utils import Util
from typing import Tuple, Dict, Any, List

class SQLiteManager:
    def __init__(self) -> None:
        self.dbname = os.path.join(os.path.dirname(__file__), "nekodata.db")
        self.get_prefixname = lambda name: os.path.splitext(name)[0]
        self.init()
    
    def init(self) -> None:
        if os.path.exists(self.dbname):
            if (Prompt().ask(
                f"[yellow] database -> [green]{self.dbname.replace(os.getcwd(),'')}[yellow] already exist, overwrite ?:", choices=['y','n'], default="y"
            ) == "n"):
                Util.log("[yellow] Abborted...[reset]")
                exit(0)
            Util.log(f"[yellow] removed -> [red]{self.dbname.replace(os.getcwd(),'')}[reset]")
            os.remove(self.dbname)
        self.connect = sqlite3.connect(self.dbname)
        self.cursor = self.connect.cursor()
                
    def isTableExist(self, tablename: str) -> bool:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?",(tablename,))
        return self.cursor.fetchone()

class TableManager(SQLiteManager):
    def __init__(self) -> None:
        super().__init__()
    
    def setGenres(self, *args: Tuple[str, str]) -> None:
        """
        -> create table
        -> set genre list to table (name, anchor) [called from loop]
        """
        if not self.isTableExist('genre_list'):
            self.cursor.execute("CREATE TABLE IF NOT EXISTS genre_list (id INTEGER PRIMARY KEY AUTOINCREMENT, genre_name VARCHAR UNIQUE, genre_id VARCHAR UNIQUE)")
            Util.log("[yellow]created[reset] table [green]`genre_list`[reset]")
        self.cursor.execute("INSERT OR IGNORE INTO genre_list (genre_name, genre_id) VALUES (?, ?)", args)
        Util.log(f"[yellow]insert[reset] {args[0]}[green]/[reset]{args[1]}")
    
    def setHanime(self, data: Dict[str, Any]) -> None:
        coverspath = Util.getdbpath("hanime/covers")
        if len(os.listdir(coverspath)) <= 1:
            Util.log("[red] covers folder data is empty!")
            return

        if not self.isTableExist("hanime_list"):
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS hanime_list (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR UNIQUE, hanimeid VARCHAR UNIQUE, durasi VARCHAR, total_episode VARCHAR, genres VARCHAR, japanese VARCHAR, jenis VARCHAR, produser VARCHAR, skor VARCHAR, status VARCHAR, tayang VARCHAR, sinopsis VARCHAR UNIQUE, cover_name VARCHAR, cover_blob BLOB)"
            )
            Util.log("[yellow]created[reset] table [green]`hanime_list`[reset]")
        self.cursor.execute(
            "INSERT INTO hanime_list (title, hanimeid, durasi, total_episode, genres, japanese, jenis, produser, skor, status, tayang, sinopsis, cover_name, cover_blob) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tuple(map(
                lambda x: data.get(x, '-'), 
                ['title', 'id', 'Durasi', 'Episode', 'Genres','Japanese', 'Jenis', 'Produser', 'Skor', 'Status', 'Tayang', 'desc']
            )) + (
                self.get_prefixname(data.get("image","")), 
                Util.loadfile(Util.getdbpath(
                    f"hanime/covers/{data.get('image')}"
                ), "bytes")
            )
        )
        Util.log(f"[yellow]insert new title -> [green]{data.get('title')}[reset]")
    
    def setEpisode(self,hanimeid: str, date: str, data: List[Dict[str, Any]]) -> None:
        thumbnailpath = Util.getdbpath("hanime/thumbnails")
        if len(os.listdir(thumbnailpath)) <= 1:
            Util.log("[red] thumbnails folder data is empty!")
            return

        if not self.isTableExist("episodes_list"):
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS episodes_list (id INTEGER PRIMARY KEY AUTOINCREMENT, hanimeid VARCHAR, episodeid VARCHAR UNIQUE, title VARCHAR, stream VARCHAR, link VARCHAR, date VARCHAR, thumbnail_alt VARCHAR UNIQUE, thumbnail BLOB UNIQUE)"
            )
            Util.log("[yellow]created[reset] table [green]`episodes_list`[reset]")
        self.cursor.execute(
            "INSERT OR IGNORE INTO episodes_list (hanimeid, episodeid, title, stream, link, date, thumbnail_alt, thumbnail) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                hanimeid,
                data.get('id', '-'), 
                data.get('thumbnail', '-').title(),
                json.dumps(data.get('stream')),
                json.dumps(data.get('link')),
                date,
                self.get_prefixname(data.get("thumbnail", "-")),
                Util.loadfile(f"{thumbnailpath}/{data.get('thumbnail')}")
            )
        )
        Util.log(f"[yellow]insert episode -> [green]{data.get('id').replace('-', ' ').title()}[reset]")

    def setPageVisitor(self):
        if not self.isTableExist("page_visitor"):
            self.cursor.execute("CREATE TABLE page_visitor (id INTEGER PRIMARY KEY, page_name VARCHAR NOT NULL UNIQUE, visit_count INTEGER DEFAULT 0)")
            Util.log("[yellow]created[reset] table [green]`page_visitor`[reset]")