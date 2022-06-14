import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, DirectoryPath, HttpUrl


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

    # Directory containing the jar file MappingService.jar for mapping proposals to the
    # database
    mapping_tool_dir: DirectoryPath

    # Directory for storing PIPT related files
    mapping_tool_pipt_dir: DirectoryPath

    # SDB username for the mapping tool
    mapping_tool_sdb_username: str

    # SDB password for the mapping tool
    mapping_tool_sdb_password: str

    # SDB URL (such as mysql://your.host:3306/your_database)
    mapping_tool_sdb_url: str

    # SSDA username for the mapping tool
    mapping_tool_ssda_username: str

    # SSDA password for the mapping tool
    mapping_tool_ssda_password: str

    # SSDA URL (such as postgresql://your.host:5432/your_database)
    mapping_tool_ssda_url: str

    # Mailchimp API key for the mapping tool
    mapping_tool_mailchimp_api_key: str

    # Mailchimp list id for the mapping tool
    mapping_tool_mailchimp_list_id: str

    # Directory for the mapping tool logs
    mapping_tool_log_dir: DirectoryPath

    # API key for the mapping tool
    mapping_tool_api_key: str

    # URL for accessing Web Manager services
    mapping_tool_web_manager_url: HttpUrl

    # URL for requesting ephemerides
    mapping_tool_ephemeris_url: HttpUrl

    # Java command
    mapping_tool_java_command: str

    # Python interpreter
    mapping_tool_python_interpreter: str

    # Finder chart tool
    mapping_tool_finder_chart_tool: str

    # Command for converting images
    mapping_tool_image_conversion_command: str

    # ?
    tcs_icd: str

    class Config:
        env_file = os.getenv("DOTENV_FILE", ".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
