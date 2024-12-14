import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from scipy.ndimage import label


# from threading import Lock

# class SingletonMeta(type):
#     """A thread-safe implementation of Singleton."""
#
#     _instances = {}
#     _lock = Lock()  # Ensure thread-safe singleton creation
#
#     def __call__(cls, *args, **kwargs):
#         with cls._lock:
#             if cls not in cls._instances:
#                 instance = super().__call__(*args, **kwargs)
#                 cls._instances[cls] = instance
#         return cls._instances[cls]


class DbgLogger:  # or DbgLogger(metaclass=SingletonMeta)
    instance = None
    msg = lambda self, *args: " ".join(map(str, args))

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if self.logger.hasHandlers():
            return

        # Ensure the directory exists
        project_root = os.path.dirname(os.path.abspath(__file__))
        print(project_root)
        log_dir = os.path.join(project_root, "log")
        os.makedirs(log_dir, exist_ok=True)

        # Create a file handler
        dt = datetime.datetime.now().strftime("%m-%d-%H:%M:%S")
        handler = TimedRotatingFileHandler(
            os.path.join(log_dir, f"{dt}.log"), when="midnight", interval=1
        )

        handler.setLevel(logging.DEBUG)

        # Create a logging format
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)

    def set_level(self, level: str):
        """
        level:
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL
        """
        LEVELS = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        self.logger.setLevel(LEVELS[level.upper()])

    def debug(self, *args):
        self.logger.debug(self.msg(*args))

    def info(self, *args):
        self.logger.info(self.msg(*args))

    def warning(self, *args):
        self.logger.warning(self.msg(*args))

    def error(self, *args):
        self.logger.error(self.msg(*args))

    def critical(self, *args):
        self.logger.critical(self.msg(*args))

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance


if __name__ == "__main__":
    logger = DbgLogger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
