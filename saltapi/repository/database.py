from sqlalchemy import create_engine

from saltapi.settings import get_settings

sdb_dsn = get_settings().sdb_dsn
echo_sql = get_settings().echo_sql

engine = create_engine(sdb_dsn, echo=echo_sql, future=True)
