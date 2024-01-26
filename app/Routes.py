#!/usr/bin/python3
# github.com/motebaya - 26.01.2023
# flask main routes handler
# file: app/Routes.py

import random
from flask import redirect, session, url_for, request
from flask_paginate import get_page_parameter, Pagination
from app.App import app, Config
from app.controllers.Home import Home
from app.controllers.Main import Main
from app.models.database.DbManager import Genres, Hanime, Episodes
from typing import Optional
from itertools import starmap

@app.route("/", methods=["GET", "POST"])
def home_index() -> str:
    return Home.index({
        "title": "Home",
        "desc": "nekopoi mirror website"
    })

@app.route("/index-list", methods=["GET", "POST"])
def list_index() -> str:
    return Main.index({
        "title": "Hanime - index list",
        "desc": "all list of hanime by letters",
        "indexs": Hanime.get_hanime_index()
    })

@app.get("/hanime/<path:hanimeid>")
def animeinfo(hanimeid: str) -> str:
    if (hanime := Hanime.get_hanime_from_id(hanimeid)):
        return Main.hanimeinfo({
            "title": f"Hanime - {hanime.title.title()}",
            "desc": hanime.sinopsis,
            "items": hanime,
            "eps": Episodes.get_episode_list(
                hanime.hanimeid
            )
        })
    else:
        if (episode := Episodes.get_episode_link(hanimeid)):
            title = episode.episodeid.replace("-", " ").title()
            return Main.hanimedownload({
                "title": f"Hanime - {title}",
                "desc": f"Download and stream {title}",
                "eps": episode
            })
        session['errormsg'] = f"Couldn't fetch ID: {hanimeid}, value not exist in database!"
        redirect(url_for("custom404"))

@app.get("/genres")
def genres_index() -> str:
    if (genres_list := Genres.get_all_genre()):
        for index, (genre_id, genre_name) in enumerate(genres_list):
            genres_list[index] = (
                genre_id,
                genre_name,
                str(len(Genres.get_hanime_from_genre(
                    genre_name
                )))
            )
    return Main.genre_list({
        "title": "Hanime - genre list",
        "desc": "list all genres",
        "genres": genres_list
    })

@app.get("/random")
def random_hanime() -> str:
    if (hanime := Hanime.get_hanime_index()):
        return redirect(url_for(
            "animeinfo", hanimeid=random.choice(hanime)[0]
        ))
    session['errormsg'] = "something error when getting list hanime.. :("
    return redirect(url_for(
        "custom404"
    ))

@app.get('/genres/<path:genre>', endpoint='genres')
@app.route("/lists", methods=["GET","POST"])
def index_item_list(genre: Optional[str | bool] = None) -> str:
    """
    -> genre/query search
    -> list genre/items
    """
    query = request.args.get("s") or request.form.get("s")
    if query and not genre:
        hanime = Hanime.get_from_query(query)
        if len(hanime) <= 1:
            genres = dict(starmap(lambda genreid, genrename: (genrename.lower(), genreid), Genres.get_all_genre()))
            if query.lower() in list(map(lambda x: x.lower(), list(genres.keys()))):
                hanime = Genres.get_hanime_from_genre(query)
            else:
                session['errormsg'] = f"Couldn't find hanime with query {query} :("
                return redirect(url_for(
                    "custom404"
                ))
    if genre and not query:
        hanime = Genres.get_hanime_from_genre(genre)
        if len(hanime) < 1:
            session['errormsg'] = f"unknow genre: {genre} ??"
            return redirect(url_for(
                "custom404"
            ))
    total = len(hanime)
    per_page = 10
    page = int(request.args.get(get_page_parameter(), 1))
    if page > total:
        session['message'] = f"invalid range page: {page}, we couldn't find anyhing :("
        return redirect(url_for(
            "custom404"
        ))
    start = (page - 1) * per_page
    end = start + per_page
    items = hanime[start:end]
    return Main.hanimelists({
        "title": f"Hanime - search for {query or genre}",
        "desc": f"hanime search show total result: {total}",
        "pagination": Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap'),
        "items": items,
        "hanime": hanime,
        "genre_to_html": Genres.genre_to_html,
        "query": query,
        "genre": genre,
        "get_hanime_from_id": Hanime.get_hanime_from_id
    })

@app.route("/404", methods=["GET", "POST"])
def custom404() -> str:
    return Home.notFound(data={
        "title": "Error - 404",
        "desc": session.get('errormsg', "something wen't wrong!")
    }), 404

@app.errorhandler(404)
def PageNotFound(error) -> str:
    return Home.notFound(error, {
        "title": f"{error.name} - {error.code}",
        "desc": error.description
    }), 404
    