import re

import inflect
from sqlalchemy import create_engine, event
from sqlalchemy.ext.automap import automap_base, generate_relationship
from sqlalchemy.orm import sessionmaker, Session
from saltapi.settings import Settings

sdb_dsn = Settings().sdb_dsn


engine = create_engine(sdb_dsn, future=True)

LocalSession = sessionmaker(bind=engine)

_pluralizer = inflect.engine()

Base = automap_base()


def _generate_relationship(base, direction, return_fn,
                           attrname, local_cls, referred_cls, **kw):
    """
    Update relationship names to avoid a cryptic error.

    Adapted from
    https://stackoverflow.com/questions/49412460/sqlalchemy-automap-backref-error.
    """
    return generate_relationship(base, direction, return_fn,
                                 attrname+'_' if "rss_etalon_config" in attrname else attrname, local_cls, referred_cls, **kw)


@event.listens_for(Base.metadata, "column_reflect")
def column_reflect(inspector, table, column_info) -> None:
    """
    Represent column names with their "uncamelized" version.

    For example, a column ProposalCode_Id is represented as pproposal_code_id.
    """

    column_name = column_info["name"]
    column_info["key"] = _uncamelize(column_name)


def _name_for_collection_relationship(base, local_cls, referred_cls, constraint) -> str:
    """
    Produce an 'uncamelized', 'pluralized' collection name based on the referred class.

    Examples: 'SomeTerm' -> 'some_terms', 'someOtherTerm -> 'some_other_terms'

    Adapted from https://docs.sqlalchemy.org/en/14/orm/extensions/automap.html.
    """

    referred_name = referred_cls.__name__
    pluralized = _pluralizer.plural(_uncamelize(referred_name))
    return pluralized


def _name_for_scalar_relationship(base, local_cls, referred_cls, constraint) -> str:
    """
    Produce an 'uncamelized', 'pluralized' collection name based on the referred class.

    Examples: 'SomeTerm' -> 'some_term', 'someOtherTerm -> 'some_other_term'
    """
    referred_name = referred_cls.__name__
    return _uncamelize(referred_name)


def _uncamelize(s: str) -> str:
    """
    'Uncamelize' a string.

    Examples: 'SomeTerm' -> 'some_term', 'someOtherTerm -> 'some_other_term'
    """
    uncamelized = re.sub(r'[A-Z]',
                         lambda m: "_%s" % m.group(0).lower(),
                         s)
    uncamelized = re.sub(r'__*', '_', uncamelized)
    if uncamelized.startswith("_"):
        uncamelized = uncamelized[1:]
    return uncamelized

Base.prepare(autoload_with=engine, generate_relationship=_generate_relationship, name_for_collection_relationship=_name_for_collection_relationship, name_for_scalar_relationship=_name_for_scalar_relationship)
