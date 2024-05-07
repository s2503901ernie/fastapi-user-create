from db.base import session_local
from db.base import Base
from db.base import engine


def launch_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()
