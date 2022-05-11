import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, DirectoryPath, FilePath, HttpUrl


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

    # Email sender
    from_email: str

    # SMTP server for sending emails
    smtp_server: str

    # Jar file with the mapping tool for mapping proposals to the database
    mapping_tool_jar: FilePath

    # Database access configuration file for the mapping tool
    mapping_tool_database_access_config: FilePath

    # Directory for the mapping tool logs
    mapping_tool_log_dir: DirectoryPath

    # Directory where the mapping tool should store proposal content
    mapping_tool_proposals_dir: DirectoryPath

    # API key for the mapping tool
    mapping_tool_api_key: str

    # Directory for storing PIPT related files
    pipt_dir: DirectoryPath

    # URL for accessing Web Manager services
    web_manager_url: HttpUrl

    # URL for requesting ephemerides
    ephemeris_url: HttpUrl

    # Java command
    java_command: str

    # Python interpreter
    python_interpreter: str

    # Finder chart tool
    finder_chart_tool: str

    # Command for converting images
    image_conversion_command: str

    class Config:
        env_file = os.getenv("DOTENV_FILE", ".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
