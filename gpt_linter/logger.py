import logging 
from gpt_linter.singleton import Singleton
class Logger(metaclass=Singleton):
    def __init__(self):
        self.logger= logging.getLogger(__name__) 
        self.logger.propagate=False

    def setup_logger(self, debug: bool) -> None:
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        log_format = "%(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.handlers = [ch]

    def __getattr__(self, attr):
        return getattr(self.logger, attr)

