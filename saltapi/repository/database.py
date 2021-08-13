from sqlalchemy import create_engine

from saltapi.settings import Settings

sdb_dsn = Settings().sdb_dsn
echo_sql = Settings().echo_sql

engine = create_engine(sdb_dsn, echo=echo_sql, future=True)
