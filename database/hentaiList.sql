PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

CREATE TABLE genre_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name VARCHAR UNIQUE,
    genre_id VARCHAR UNIQUE
);

CREATE TABLE hentai_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR UNIQUE,
    hentai_id VARCHAR UNIQUE,
    durasi VARCHAR,
    total_episode VARCHAR,
    genres VARCHAR,
    japanese VARCHAR,
    jenis VARCHAR,
    produser VARCHAR,
    skor VARCHAR,
    status VARCHAR,
    tayang VARCHAR,
    sinopsis VARCHAR UNIQUE,
    image_name VARCHAR,
    image_cover BLOB
);

CREATE TABLE episodes_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hentai_id VARCHAR,
    episode_id VARCHAR UNIQUE,
    title VARCHAR,
    stream VARCHAR,
    link VARCHAR,
    date VARCHAR,
    thumbnail_alt VARCHAR UNIQUE,
    thumbnail BLOB UNIQUE
);

CREATE TABLE page_visitor (
    id INTEGER PRIMARY KEY,
    page_name VARCHAR NOT NULL UNIQUE,
    visit_count INTEGER DEFAULT 0
);

COMMIT;