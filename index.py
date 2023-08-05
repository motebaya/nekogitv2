#!/usr/bin/env python3
"""
author: @github.com/motebaya
date: 2023.06.11 - 11.49 PM
file: index.py
app: flask
"""

import os, json, base64
from flask import (
    Flask,
    request,
    render_template,
    url_for,
    redirect,
    flash,
    session
)
from flask_paginate import (
    Pagination,
    get_page_parameter
)
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from typing import List, Optional
load_dotenv()

app = Flask(
    __name__,
    static_url_path="",
    static_folder="public",
    template_folder="templates"
)
app.config['DEBUG'] = True
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
    os.environ.get('DBPATH')
)
db = SQLAlchemy(app)
app.app_context().push()

"""
ORM database with sqlite3
"""
class Genres(db.Model):
    __tablename__ = 'genre_list'
    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.Text, unique=True)
    genre_id = db.Column(db.Text, unique=True)

    def __repr__(self):
        return f"<Genres {self.__tablename__}>"

    @staticmethod
    def get_genres_list() -> List['Genres']:
        """
        return all genres list from table
        """
        return Genres.query.all()
    
    @staticmethod
    def get_genres(genre: str) -> List['Genres']:
        """
        return anime list if genre contain it.
        """
        genre = genre.replace('-', ' ')
        return Hanime.query.filter(
            func.lower(
                Hanime.genres).like(
                    f"%{genre.lower()}%"
                )
            ).all()
    
    @staticmethod
    def format_genre(genre: str) -> str:
        """
        format genre list to html hyperlink
        """
        if genre:
            return ''.join(map(
                lambda x: "<a href='/genres/{}' rel='noopener'>{}</a>, ".format(
                    x.lower(), x.strip()
                ), genre.split(', ')
            )).strip(', ')
        return ""

"""
hentai list table
"""
class Hanime(db.Model):
    __tablename__ = 'hentai_list'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    hentai_id = db.Column(db.String(100), unique=True)
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
    image_name = db.Column(db.String(100))
    image_cover = db.Column(db.LargeBinary)
    
    def __repr__(self):
        return f"<Hanime: on table {self.__tablename__}>"

    @staticmethod
    def get_hentai_list() -> List['Hanime']:
        return Hanime.query.all()

    @staticmethod
    def get_anime_id(animeid: str) -> 'Hanime':
        """
        get all anime info with id: eg. 'toriko-no-chigiri'
        """
        return Hanime.query.filter_by(
            hentai_id=animeid
        ).first()

    @staticmethod
    def search_title(title: str) -> List['Hanime']:
        """
        search anime title by anything string: eg. 'boku'
        """
        title = f"%{title.lower()}%"
        return Hanime.query.filter(
            or_(
                func.lower(Hanime.title).like(title),
                func.lower(Hanime.sinopsis).like(title)
            )
        ).all()

class Episodes(db.Model):
    __tablename__ = "episodes_list"
    id = db.Column(db.Integer, primary_key=True)
    hentai_id = db.Column(db.String(100))
    episode_id = db.Column(db.String(225), unique=True)
    title = db.Column(db.String(225), unique=True)
    stream = db.Column(db.Text)
    link = db.Column(db.Text)
    date = db.Column(db.String(225))
    thumbnail_alt = db.Column(db.String(225), unique=True)
    thumbnail = db.Column(db.LargeBinary)
    
    def __repr__(self):
        return f"<Episodes: {self.__tablename__}>"
    
    @staticmethod
    def get_episode_list(animeid: str) -> List['Episodes']:
        """
        get hentai list with hentai id, eg: this-anime-title
        """
        return Episodes.query.filter_by(
            hentai_id=animeid
        ).all()

    @staticmethod
    def get_episode(episodeid: str) -> List['Episodes']:
        """
        get episode by eps id , eg: anime-title-sub-indo-eps-1
        """
        return Episodes.query.filter_by(
            episode_id=episodeid
        ).first()

"""
page visitor table
"""
class PageVisitor(db.Model):
    __tablename__ = 'page_visitor'
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(200), unique=True, nullable=False)
    visit_count = db.Column(db.Integer, default=0)

    @staticmethod
    def get_total(page_name: str) -> Optional['PageVisitor']:
        """
        get total page visited -> int
        """
        return PageVisitor.query.filter_by(
            page_name=page_name
        ).first()

"""
router handler
"""
@app.get('/anime/<path:animeid>')
def anime_info(animeid: str):
    """
    route for anime/<animeinfo> or anime/<anime eps>
    """
    if (anime_set := Hanime.get_anime_id(animeid)):
        episode_list = Episodes.get_episode_list(animeid)
        show_episode = Episodes.get_episode(animeid)
        return render_template(
            'anime_info.html', 
            items=anime_set, 
            episode_list=episode_list, 
            isepisode=show_episode,
            loadjson_string=json.loads,
            encode_image=base64.b64encode
        )
    else:
        if (anime_set := Episodes.get_episode(animeid)):
            return render_template(
                'anime_info.html',
                items=anime_set,
                isepisode=True,
                loadjson_string=json.loads,
                get_anime_id=Hanime.get_anime_id,
                encode_image=base64.b64encode
            )

        session['message'] = "nothing anime: {} in database".format(
            animeid.replace(
                '-', ' '
            ).title()
        )
        return redirect(
            url_for(
                'page_not_found',
            )
        )

@app.route('/genre-list', methods=['GET', 'POST'])
def genre_list():
    """
    render all genres to view, leave if can't get genre list
    """
    total_visit = PageVisitor.get_total('genres')
    if not total_visit:
        db.session.add(PageVisitor(page_name='genres'))
    else:
        total_visit.visit_count += 1
    db.session.commit()
    if (all_genres := Genres.get_genres_list()):
        return render_template(
            'genre-list.html', items=all_genres, total_visit=total_visit.visit_count if total_visit.visit_count is not None else 0
        )
    session['message'] = 'Nothing Genres database!'
    return redirect(
        url_for(
            'page_not_found'
        )
    )

@app.get('/genres/<path:genre>', endpoint='genres')
@app.route('/hentai-list', methods=['GET', 'POST'])
def hentai_list(genre: str = None):
    """
    genre set or search query? this will do that!
    """
    if request.method == "POST":
        form_title = request.form.get('s')

    if request.method == "GET":
        form_title = request.args.get('s')

    """
    handle query search
    """
    if form_title and not genre:
        if (result := Hanime.search_title(form_title)):
            length = len(result)
        else:
            session['message'] = f"Query: {form_title} not found in database!"
            return redirect(
                url_for(
                    'page_not_found'
                )
            )

    """
    handle selected genre
    """
    if genre and not form_title:
        if (result := Genres.get_genres(genre)):
            length = len(result)
        else:
            session['message'] = f"Genre: {genre} not found in database!"
            return redirect(
                url_for(
                    'page_not_found'
                )
            )

    """
    show all list if genre and title is nothing
    """
    if not form_title and not genre:
        if (result := Hanime.get_hentai_list()):
            length = len(result)
        else:
            session['message'] = "Error: database is empty!"
            return redirect(
                url_for(
                    'page_not_found'
                )
            )

    total_visit = PageVisitor.get_total('hentai-list')
    if not total_visit:
        db.session.add(PageVisitor(page_name='hentai-list'))
    else:
        total_visit.visit_count += 1
    db.session.commit()

    per_page = 10
    page = int(request.args.get(get_page_parameter(), 1))
    """
    go out if user input manual page query e.g: ?page=9999
    """
    if page > length:
        session['message'] = "Invalid page <{}> bruh. ".format(
            str(page)
        )
        return redirect(
            url_for(
                'page_not_found'
            )
        )

    start = (page - 1) * per_page
    end = start + per_page
    items = result[start:end]

    pagination = Pagination(
        page=page,
        total=length,
        per_page=per_page,
        css_framework='bootstrap'
    )

    return render_template(
        "hentai-list.html",
        items=items,
        pagination=pagination,
        result=result,
        s=form_title,
        g=genre,
        genre_formatter=Genres.format_genre,
        total=str(length),
        encode_image=base64.b64encode,
        total_visit=total_visit.visit_count
    )

"""
index or home
"""
@app.route('/', methods=['POST', 'GET'])
def index():
    visited = PageVisitor.get_total('home')
    if not visited:
        db.session.add(
            PageVisitor(
                page_name='home'
            )
        )
    else:
        visited.visit_count += 1
    db.session.commit()

    return render_template(
        "index.html", total_visit=visited.visit_count
    )

"""
comming soon
"""
@app.route('/comming-soon', methods=['GET', 'POST'])
def comming_soon():
    return render_template(
        'comming_soon.html'
    )

"""
page error handle
"""
@app.errorhandler(404)
def page_error(error):
    if 'message' not in session:
        session['message'] = "Page your visited not found"
    return redirect(
        url_for(
            'page_not_found'
        )
    )

@app.route('/404')
def page_not_found():
    flash(
        session.get('message'),
        'error'
    )
    return render_template(
        "page_error.html"
    )

if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT"))
    )
