from sqlalchemy import create_engine

from saltapi.settings import Settings

sdb_dsn = Settings().sdb_dsn


engine = create_engine(sdb_dsn, echo=False, future=True)
