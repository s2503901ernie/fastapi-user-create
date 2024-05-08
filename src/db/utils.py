from fastapi import HTTPException
import logging

from db.base import session_local


logger = logging.getLogger(__name__)


def get_db():
    database = session_local()
    try:
        yield database
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(str(e))
        database.rollback()
    finally:
        database.close()
