import os
import logging
import sentry_sdk

from dotenv import load_dotenv

from loguru import logger

from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from sentry_sdk.integrations.logging import (
    BreadcrumbHandler,
    EventHandler,
)

from saltapi.settings import Settings


load_dotenv()


class InterceptHandler(logging.Handler):
    """Intercepts builtin logging messages and routes them to Loguru

    reference: https://loguru.readthedocs.io/en/stable/overview.html#customizable-levels
    """

    def emit(self, record) -> None:

        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(app):
    if Settings().sentry_dsn:
        logger.add(
            BreadcrumbHandler(level=logging.DEBUG),
            level=logging.DEBUG,
        )

        logger.add(
            EventHandler(level=logging.ERROR),
            level=logging.ERROR,
        )

        sentry_sdk.init(dsn=Settings().sentry_dsn)
        sentry_app = SentryAsgiMiddleware(app)

    else:
        logging.warning('SENTRY_DSN variable is not set.')

    # Enable interceptor
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

