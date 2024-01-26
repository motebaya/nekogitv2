#!/usr/bin/python3
# github.com/motebaya - 22.01.2023
# utilities helper
# file: app/models/helpers/Utils.py

import os, json, time, io, httpx
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    BarColumn, 
    TextColumn, 
    DownloadColumn, 
    TransferSpeedColumn, 
    TimeRemainingColumn
)

class Util:
    logger = None

    @staticmethod
    def download(url: str, fname: str) -> str:
        # https://www.python-httpx.org/quickstart/#streaming-responses
        isexist = False
        with httpx.Client(headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}) as client:
            if not os.path.exists(fname):
                with client.stream("GET", url) as response:
                    with io.open(fname, "wb") as f:
                        with Progress(SpinnerColumn(speed=1.5),
                            TextColumn("[green] Downloading..", justify="right"),
                            BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%",
                            DownloadColumn(binary_units=False),
                            TransferSpeedColumn(),
                            TimeRemainingColumn(),
                            console=Console(),
                            transient=True
                        ) as progress:
                            task = progress.add_task("[green] Downloading..", total=int(response.headers.get('content-length', 0)))
                            for content in response.iter_bytes():
                                f.write(content)
                                progress.update(task, advance=len(content))
                            f.close()
                            progress.stop()
                    Util.log(f"[green]Completed..saved as: [blue]{fname.replace(os.getcwd(), '')}")
            else:
                isexist = True
                Util.log(f"[red]skipping.. [blue]{os.path.basename(fname)} [green]file exist!")
            return os.path.basename(fname), isexist
    
    @staticmethod
    def show_info(info: dict, title: Optional[str] = "info") -> None:
        Console().print(Panel.fit('\n'.join(map(
                lambda x: f"[white]{x[0].title()}[blue]: [white]{x[1]}",
                dict(sorted(
                    info.items()
                )).items()
            )),  title=f"[white] {title}",
            border_style="yellow"
        ))

    @staticmethod
    def log(msg: str) -> None:
        Console().print(
            " [cyan]{} [reset]{}".format(
                time.ctime().split()[-2], msg
            ), style="not bold"
        )
    
    @staticmethod
    def getdbpath(file: str) -> str:
        return os.path.realpath(os.path.join(
            os.path.dirname(__file__),
                f"../database/{file}"
        ))

    @staticmethod
    def saveto(content: str | dict, path: str) -> None:
        Util.logger.info(f"saving {len(str(content))} content to::{path.replace(os.getcwd(), '')}")
        with io.open(path, 'w') as f:
            f.write(
                str(content) if isinstance(
                    content, str
                ) else json.dumps(
                    content
                )
            )

    @staticmethod
    def loadfile(file: str, ftype: Optional[str] = '') -> str | bytes | dict:
        with io.open(file, mode="rb" if ftype.lower() not in ['dict', 'str'] else "r") as f:
            content = f.read()
        return content if ftype != 'dict' else\
            json.loads(content)
    
    @staticmethod
    def path_exist(path: str) -> bool:
        return os.path.exists(path) and os.path.getsize(
            path
        ) > 1
