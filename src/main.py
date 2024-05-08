from fastapi import FastAPI
import logging
import pathlib
import os
import subprocess

from routers.user import router as users_router


ROOT_PATH = pathlib.Path(os.getcwd())
ALEMBIC_PATH = ROOT_PATH.joinpath('db')


def migrate_db_schema():
    """Alpha database migration."""
    try:
        subprocess.run(
            args=['python3', '-m', 'alembic', 'upgrade', 'head'],
            cwd=ALEMBIC_PATH,
        )
    except subprocess.CalledProcessError as e:
        logging.warning('Please drop all tables when the first time of this error occurs.')
        raise e


migrate_db_schema()
app = FastAPI()

# Add routers
app.include_router(users_router)


@app.get("/")
def read_root():
    return "Server is running."
