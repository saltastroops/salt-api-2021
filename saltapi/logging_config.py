import os
import logging

import sentry_sdk
from dotenv import load_dotenv

from loguru import logger

from sentry_sdk.integrations.logging import (
    LoggingIntegration,
    BreadcrumbHandler,
    EventHandler,
)

load_dotenv()

LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    """Intercepts builtin logging messages and routes them to Loguru"""

    def emit(self, record) -> None:

        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # find calle from where the message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    if os.getenv('SENTRY_DSN'):
        _ = logger.add(
            BreadcrumbHandler(level=logging.DEBUG),
            level=logging.DEBUG,
        )

        _ = logger.add(
            EventHandler(level=logging.ERROR),
            level=logging.ERROR,
        )

        sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'),
                        integrations=[
                            LoggingIntegration(level=None, event_level=None)
                        ])

    # enable inteceptor
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

