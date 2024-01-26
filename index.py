#!/usr/bin/python3
# @github.com/motebaya - 12.01.2024
# index

from app.Routes import app, Config

if __name__=="__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT
    )