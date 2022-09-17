import logging.config
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + "/../"

LOG_DIR = BASE_DIR + "/logs"

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "verbose": {
                "format": "[%(asctime)s][%(levelname)s] %(module)s: %(message)s"
            },
            "simple": {"format": "%(levelname)s: %(message)s"},
        },
        "handlers": {
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_DIR + "/intel.log",
                "maxBytes": 1024 * 1024 * 2,
                "backupCount": 50,
                "formatter": "verbose",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "who": {
                "level": "DEBUG",
                "propagate": True,
                "handlers": ["console", "file"],
            },
            "paramiko": {
                "level": "INFO",
                "propagate": True,
                "handlers": ["console", "file"],
            },
            "portalocker": {
                "level": "INFO",
                "propagate": True,
                "handlers": ["console", "file"],
            },
            "watchdog": {
                "level": "INFO",
                "propagate": True,
                "handlers": ["console", "file"],
            },
            "filewatcher": {
                "level": "INFO",
                "propagate": True,
                "handlers": ["console", "file"],
            },
            "apscheduler": {
                "level": "INFO",
                "propagate": True,
                "handlers": ["console", "file"],
            },
            "scheduler": {
                "level": "INFO",
                "propagate": True,
                "handlers": ["console", "file"],
            },
            "notification": {
                "level": "INFO",
                "propagate": True,
                "handlers": ["console", "file"],
            },
        },
    }
)
