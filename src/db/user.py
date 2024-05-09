from typing import Union

from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session

from db.base import Base


class DBUser(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    password_hash: Mapped[str]


def create_db_user(name: str, password_hash: str, session: Session) -> DBUser:
    db_user = DBUser(name=name, password_hash=password_hash)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_db_user(name: str, session: Session, password_hash: str = None) -> Union[DBUser, None]:
    query = session.query(DBUser).filter(DBUser.name == name)
    if password_hash is not None:
        query = query.filter(DBUser.password_hash == password_hash)
    db_user = query.first()
    return db_user
