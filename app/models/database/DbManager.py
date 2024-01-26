#!/usr/bin/env python3
# @githhub.com/motebaya - 23.01.2024
# sql orm database manager
from __future__ import annotations
from app.App import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from typing import List, Tuple, Any, Dict, Optional
from itertools import starmap
from trycast import isassignable

db = SQLAlchemy(app)
app.app_context().push()


class Episodes(db.Model):
    __tablename__ = "episodes_list"
    id = db.Column(db.Integer, primary_key=True)
    hanimeid = db.Column(db.String(100))
    episodeid = db.Column(db.String(225), unique=True)
    title = db.Column(db.String(225), unique=True)
    stream = db.Column(db.Text)
    link = db.Column(db.Text)
    date = db.Column(db.String(225))
    thumbnail_alt = db.Column(db.String(225), unique=True)
    thumbnail = db.Column(db.LargeBinary)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            column.name: getattr(self, column.name)\
                for column in self.__table__.columns
        }

    @staticmethod
    def get_episode_list(hanimeid: str) -> List[Episodes]:
        return Episodes.query.filter_by(
            hanimeid=hanimeid
        ).all()

    @staticmethod
    def get_episode_link(episodeid: str) -> List[Episodes]:
        return Episodes.query.filter_by(
            episodeid=episodeid
        ).first()

class Hanime(db.Model):
    __tablename__ = 'hanime_list'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    hanimeid = db.Column(db.String(100), unique=True)
    durasi = db.Column(db.String(20))
    total_episode = db.Column(db.String(3))
    genres = db.Column(db.String(255))
    japanese = db.Column(db.String(100))
    jenis = db.Column(db.String(20))
    produser = db.Column(db.String(100))
    skor = db.Column(db.String(10))
    status = db.Column(db.String(10))
    tayang = db.Column(db.String(20))
    sinopsis = db.Column(db.Text, unique=True)
    cover_name = db.Column(db.String(100))
    cover_blob = db.Column(db.LargeBinary)
    
    # it's more simply and readable
    # https://stackoverflow.com/a/1958219/
    @staticmethod
    def to_dict(self) -> Dict[str, Any]:
        return {
            column.name: getattr(self, column.name)\
                for column in self.__table__.columns
        }
    
    @staticmethod
    def get_hanime_index() -> List[Tuple[str, str]]:
        return list(map(
            lambda x: (x.hanimeid, x.title),
            Hanime.query.with_entities(
                Hanime.hanimeid, Hanime.title
            ).all()
        ))

    @staticmethod
    def get_hanime_list() -> List[Hanime]:
        return Hanime.query.all()

    @staticmethod
    def get_hanime_from_id(animeid: str) -> Hanime:
        return Hanime.query.filter_by(
            hanimeid=animeid
        ).first()

    @staticmethod
    def get_from_query(title: str) -> List[Hanime]:
        title = f"%{title.lower()}%"
        fhanime = Hanime.query.filter(or_(
            func.lower(Hanime.title).like(title),
            func.lower(Hanime.sinopsis).like(title)
        )).all()
        if (len(fhanime) != 0):
            fhanime.extend(
                Episodes.query.filter(or_(
                    func.lower(Episodes.episodeid).like(title)
                )).all()
            )
        return fhanime
        

class Genres(db.Model):
    __tablename__ = 'genre_list'
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.Text, unique=True)
    genre_id = db.Column(db.Text, unique=True)

    @staticmethod
    def get_all_genre() -> List[Tuple[str, str]]:
        return Genres.query.with_entities(
            Genres.genre_id, Genres.genre_name
        ).all()
    
    @staticmethod
    def genre_to_html(genre: str, highlight: Optional[str] = '') -> str:
        if genre:
            if isassignable(genre, List[Tuple[str, str]]):
                return ''.join(starmap(
                    lambda genre_id, genre_name: "<a href='/genres/{}' rel='noopener noreferer'>{}</a>, ".format(
                        genre_id.lower(), genre_name.strip()
                    ), genre
                )).strip(', ')

            if isinstance(genre, str):
                allgenres = dict(starmap(lambda genreid, genrename: (genrename, genreid), Genres.get_all_genre()))
                return ''.join(map(
                    lambda genre_: "<a href='/genres/{}' {} rel='noopener'>{}</a>, ".format(
                        allgenres.get(genre_, "#"), "class='bg-warning navbar-brand fw-medium'" if \
                          allgenres.get(genre_, "#") == highlight else '', genre_.strip()
                    ), genre.split(", ")
                )).strip(", ")
                # formated = []
                # for genre_ in genre.split(', '):
                #     if allgenres.get(genre_, "#") == highlight:
                #         formated.append(
                #           "<a href='/genres/{}' class='bg-warning navbar-brand fw-medium' rel='noopener'>{}</a>, ".format(
                #               allgenres.get(genre_, "#"), genre_.strip()
                #           )
                #         )
                #     else:
                #         formated.append(
                #           "<a href='/genres/{}' rel='noopener'>{}</a>, ".format(
                #             allgenres.get(genre_, "#"), genre_.strip()
                #           )
                #         )
                # return ''.join(formated).strip(", ")
        return ""

    @staticmethod
    def get_hanime_from_genre(genre: str) -> List[Genres]:
        genre = genre.replace('-', ' ')
        return Hanime.query.filter(
            func.lower(
                Hanime.genres).like(
                    f"%{genre.lower()}%"
                )
            ).all()
    
class PageVisitor(db.Model):
    __tablename__ = 'page_visitor'
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(200), unique=True, nullable=False)
    visit_count = db.Column(db.Integer, default=0)

    @staticmethod
    def get_total(page_name: str) -> Optional[PageVisitor]:
        return PageVisitor.query.filter_by(
            page_name=page_name
        ).first()