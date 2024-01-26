#!/usr/bin/python3
# @github.com/motebaya - 2023.06.3 08:42:53 AM
# file: __logger__

import logging
from colorama.ansi import Fore

logging.addLevelName(logging.WARNING, f"{Fore.YELLOW}warning{Fore.RESET}")
logging.addLevelName(logging.DEBUG, f"{Fore.GREEN}debug{Fore.RESET}")
logging.addLevelName(logging.INFO, f"{Fore.CYAN}info{Fore.RESET}")

class Logger:
    
    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING
    }
    
    @staticmethod
    def getLogger(level: str) -> logging.RootLogger:
        logging.basicConfig(**{
            "format": f" {Fore.CYAN}%(asctime)s{Fore.RESET} %(levelname)s{Fore.CYAN}::{Fore.RESET}%(message)s ",
            "level": Logger.levels.get(level) or "info",
            "datefmt": '%H:%M:%S'
        })
        return logging.getLogger(__name__)
