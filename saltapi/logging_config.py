import logging
from types import FrameType
from typing import Union, cast

import sentry_sdk
from fastapi import FastAPI
from loguru import logger
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import BreadcrumbHandler, EventHandler

from saltapi.settings import Settings


class InterceptHandler(logging.Handler):
    """Intercepts builtin logging messages and routes them to Loguru

    reference: https://loguru.readthedocs.io/en/stable/overview.html#customizable-levels
    """

    def emit(self, record: logging.LogRecord) -> None:

        # Get corresponding Loguru level if it exists
        try:
            level: Union[str, int] = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(app: FastAPI) -> None:
    sentry_dsn = Settings().sentry_dsn
    if sentry_dsn:
        logger.add(
            BreadcrumbHandler(level=logging.DEBUG),
            level=logging.DEBUG,
        )

        logger.add(
            EventHandler(level=logging.ERROR),
            level=logging.ERROR,
        )

        sentry_sdk.init(dsn=sentry_dsn)
        SentryAsgiMiddleware(app)

    else:
        logging.warning("SENTRY_DSN variable is not set.")

    # Enable interceptor
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
