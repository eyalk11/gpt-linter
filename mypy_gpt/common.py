
import difflib
import logging
import os
from typing import Tuple, Iterable

def setup_logger(logger: logging.Logger, debug: bool) -> None:
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    log_format = "%(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.handlers = [ch]

def generate_diff(original_content: str, new_content: str, path: str) -> Tuple[str, str]:
    try:
        from colorama import Fore, init
        init()
    except ImportError:  # fallback so that the imported classes always exist
        class ColorFallback():
            __getattr__ = lambda self, name: ''

        Fore = ColorFallback()

    def color_diff(diff: Iterable[str]) -> Iterable[str]:
        for line in diff:
            if line.startswith('+'):
                yield Fore.GREEN + line + Fore.RESET
            elif line.startswith('-'):
                yield Fore.RED + line + Fore.RESET
            elif line.startswith('^'):
                yield Fore.BLUE + line + Fore.RESET
            elif line.startswith('@@'):
                yield Fore.BLUE + line[:line.rindex('@@')+2] + Fore.RESET
            else:
                yield line

    diffres = list(difflib.unified_diff(original_content.split('\n'), new_content.split('\n'), fromfile=path, tofile=path+"b", lineterm=''))
    return os.linesep.join(color_diff(diffres)), os.linesep.join(diffres)
