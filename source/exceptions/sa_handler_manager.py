from loguru import logger
from psycopg2 import errorcodes
from psycopg2.errorcodes import FOREIGN_KEY_VIOLATION, UNIQUE_VIOLATION, lookup
from sqlalchemy.exc import NoResultFound, SQLAlchemyError


class ItemNotFound(SQLAlchemyError):
    ...


class ItemNotUnique(SQLAlchemyError):
    ...


class ErrorHandler:

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_instance, traceback):
        if not ex_instance:
            return
        logger.error(ex_instance)
        if hasattr(ex_instance, 'orig'):
            match ex_instance.orig.pgcode:
                case errorcodes.UNIQUE_VIOLATION:
                    raise ItemNotUnique("Not unique")
                case errorcodes.FOREIGN_KEY_VIOLATION:
                    raise SQLAlchemyError("Foreign key not present")
                case _:
                    raise ex_instance
        elif type(ex_instance) == NoResultFound:
            raise ItemNotFound
        elif ex_instance:
            raise ex_instance
        else:
            pass
