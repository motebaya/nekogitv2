#!/usr/bin/env python3
# SQLite3 database creation
# date: 2023-06-22 11:58:49 PM
# author: @github.com/motebaya
# official docs -> https://docs.python.org/3/library/sqlite3.html
# file: CreateDb.py

import sqlite3, os, json
from nekopoiv2 import logger, logging, delay
from typing import Union, Tuple, Dict, Collection, List
from rich.prompt import Prompt

class SQLite3(object):
    def __init__(self, database: str = 'hentai') -> None:
        self.connect = None
        self.cursor = None
        self.db_path: str = os.path.join(os.path.realpath("./database/"), "nekopoi.json")
        self.dbname = "{}/{}List.db".format(
            os.path.dirname(self.db_path), database
        )
        if not os.path.exists(self.db_path):
            logger.warning('You don"t have database!')
            exit(1)
        self.initialize()
    
    def readAsJson(self) -> dict:
        """
        open db json

        Returns:
            dict: json db content
        """
        return json.loads(open(
            self.db_path
        ).read())

    def initialize(self):
        """
        connect sqlite3 db. if you already .db (sqlite database) this will ask you to confirm,
        you want to delete then create again or not.
        TODO:
            - connect to sqlite3 with dbname.
        """
        if os.path.exists(self.dbname):
            confirm_delete = Prompt().ask(
                f"database: {self.dbname} already exist, continue (recreate)?",
                choices=['y', 'n'], default='n'
            )
            if confirm_delete == 'n':
                logger.warning(f"leave: {self.dbname}")
                exit(1)

            os.remove(self.dbname)
            logger.warning(f"Database: {self.dbname} has removed!")
                
        self.connect = sqlite3.connect(self.dbname)
        self.cursor = self.connect.cursor()
    
    def get_binary(self, binary_path: str = '') -> Union[bytes, None]:
        """
        open binary image path.

        Args:
            binary_path (str, optional): filepath. Defaults to ''.

        Returns:
            Union[bytes, None]: return as 
        """
        if os.path.exists(binary_path):
            with open(binary_path, "rb") as f:
                return f.read()
        return None

    def check_table(self, tablename: str) -> bool:
        """
        check user table from sqlite_master table

        Args:
            tablename (str): tablename

        Returns:
            bool: True if exists & vice versa
        """
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (tablename,)
        )
        return self.cursor.fetchone()

class Create_db(SQLite3):
    """
    nekopoi.care database clas handler
    """
    def __init__(self, database: str) -> None:
        super().__init__(database)
    
    def set_genre(self, *args: Tuple[str, str]) -> None:
        """_set items to table genre list_
        
        TODO: check table, if not exits then create it.
              insert genre name and genre slug to table.
        """
        if not self.check_table('genre_list'):
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS genre_list (id INTEGER PRIMARY KEY AUTOINCREMENT, genre_name VARCHAR UNIQUE, genre_id VARCHAR UNIQUE)",
            )
            logger.info("CREATE new table:: genre_list")

        self.cursor.execute(
            "INSERT OR IGNORE INTO genre_list (genre_name, genre_id) VALUES (?, ?)",
            args
        )
        logger.info(f"INSERT :: {args[0]} -> {args[1]}")
    
    def set_hentai(self, data: Dict[str, str]) -> None:
        """
        create tables hentai_list from hentai list

        Args:
            data (_type_): dict
        """
        if not self.check_table('hentai_list'):
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS hentai_list (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR UNIQUE, hentai_id VARCHAR UNIQUE, durasi VARCHAR, total_episode VARCHAR, genres VARCHAR, japanese VARCHAR, jenis VARCHAR, produser VARCHAR, skor VARCHAR, status VARCHAR, tayang VARCHAR, sinopsis VARCHAR UNIQUE, image_name VARCHAR, image_cover BLOB)"
            )
            logger.info("CREATE new TABLE :: hentai_list")
        
        """
        query set
        """
        self.cursor.execute(
            "INSERT INTO hentai_list (title, hentai_id, durasi, total_episode, genres, japanese, jenis, produser, skor, status, tayang, sinopsis, image_name, image_cover) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tuple(map(
                lambda x: data.get(x, '-'), 
                ['title', 'id', 'Durasi', 'Episode', 'Genres','Japanese', 'Jenis', 'Produser', 'Skor', 'Status', 'Tayang', 'desc']
            )) + (
                os.path.splitext(
                    data.get('image', '-')
                )[0], self.get_binary(
                    os.path.join('./database/hentai/cover/', data.get('image'))
                )
            )
        )
        logger.info(f"INSERT new :: {len(data)} rows")
    
    def set_episode(self, hentai_id: str, eps_data: List[Dict[str, Collection[str]]], date: str) -> None:
        """
        create tables episodes_list from list episode

        Args:
            anime_id (str): unique hentai id
            episode_data (dict): dict
            date (str): str -> release date
        """
        if not self.check_table('episodes_list'):
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS episodes_list (id INTEGER PRIMARY KEY AUTOINCREMENT, hentai_id VARCHAR, episode_id VARCHAR UNIQUE, title VARCHAR, stream VARCHAR, link VARCHAR, date VARCHAR, thumbnail_alt VARCHAR UNIQUE, thumbnail BLOB UNIQUE)"
            )
            logger.info("CREATE new TABLE :: episodes_list")
        
        """_summary_
        insert eps rows
        """
        self.cursor.execute(
            "INSERT OR IGNORE INTO episodes_list (hentai_id, episode_id, title, stream, link, date, thumbnail_alt, thumbnail) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                hentai_id, eps_data.get('id'), eps_data.get('thumbnail', '-').replace(
                    '-', ' ').title(), 
                json.dumps(eps_data.get('stream')),
                json.dumps(eps_data.get('link')),
                date, os.path.splitext(
                    eps_data.get('thumbnail', '-')
                )[0], self.get_binary(os.path.join(
                    './database/hentai/thumbnail/', eps_data.get('thumbnail')
                ))
            )
        )
        logger.info(f"INSERT new :: {len(eps_data)} rows.")

    def set_jav(self, data: Dict[str, object]) -> None:
        """
        database create for jav list

        Args:
            data (Dict[str, object]): _description_
        (currently no need)
        """
        return

    def create_visitorTable(self):
        """
        each page have count, how much page viewed.
        """
        if not self.check_table('page_visitor'):
            self.cursor.execute(
                "CREATE TABLE page_visitor (id INTEGER PRIMARY KEY, page_name VARCHAR NOT NULL UNIQUE, visit_count INTEGER DEFAULT 0)"
            )
            logger.info('Create new table :: page_visitor')