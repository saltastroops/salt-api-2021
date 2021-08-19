import os
from typing import Optional

from pydantic import BaseSettings, DirectoryPath


class Settings(BaseSettings):
    """
    Settings for the Web Manager.

    Every setting must be defined as an environment variable (or in an .env file at the
    root level of the project). The environment variable names may be in uppercase.
    """

    # Directory containing all the proposal directories
    proposals_dir: DirectoryPath

    # DSN for the SALT Science Database, in a format understood by SQL Alchemy
    # Example: mysql+pymysql://user:password@database.server:3306/sdb
    sdb_dsn: str

    # Echo all executed SQL statements?
    echo_sql: bool = False

    # Secret key for encoding JWT tokens
    # Should be generated with openssl: openssl rand -hex 32
    secret_key: str

    # URI which is allowed to connect to the API
    frontend_uri: str

    # DSN for Sentry
    sentry_dsn: Optional[str]

    # Hashing algorithm.
    algorithm: str

    class Config:
        env_file = os.getenv("DOTENV_FILE", ".env")
