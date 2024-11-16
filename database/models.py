from datetime import datetime, date
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DATE, ARRAY, ForeignKey
from sqlalchemy import Integer, Boolean, String, VARCHAR, TIMESTAMP, text, Column

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

NOW_AT_UTC = text("timezone('utc', now())")

class Base(DeclarativeBase):
    pass

metadata = MetaData(naming_convention=convention)


class User(Base):
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    created_at: datetime = Column(TIMESTAMP(timezone=False), server_default=NOW_AT_UTC,
                                                 nullable=True, autoincrement=True)
    update_at: datetime = Column(TIMESTAMP(timezone=False), server_default=NOW_AT_UTC,
                                                nullable=True, onupdate=NOW_AT_UTC, autoincrement=True)
    deleted_at: datetime = Column(TIMESTAMP(timezone=False), nullable=True)
    username: str = Column(VARCHAR, nullable=False)
    password_hash: str = Column(VARCHAR, nullable=False)
    phone: str = Column(String, nullable=False)
    preferences: list = Column(ARRAY(Integer), nullable=True)
    refresh_token: str = Column(String, nullable=True)


class GroupsEvent(Base):
    __tablename__ = "group_event"
    id: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(TIMESTAMP(timezone=False), server_default=NOW_AT_UTC,
                                            nullable=True, autoincrement=True)
    update_at: datetime = Column(TIMESTAMP(timezone=False), server_default=NOW_AT_UTC,
                                            nullable=True, autoincrement=True)
    deleted_at: datetime = Column(TIMESTAMP, nullable=True)
    name: str = Column(VARCHAR, nullable=False)
    description: str = Column(VARCHAR, nullable=True)


class UsersGroup(Base):
    __tablename__ = "user_group"
    id: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(TIMESTAMP, nullable=False, autoincrement=True)
    update_at: datetime = Column(TIMESTAMP, nullable=False, autoincrement=True)
    deleted_at: datetime = Column(TIMESTAMP)
    main_user: int = Column(Integer, ForeignKey("user.id"))
    group_members: list = Column(ARRAY(Integer))


class Events(Base):
    __tablename__ = "event"
    id: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(TIMESTAMP, nullable=False, autoincrement=True)
    update_at: datetime = Column(TIMESTAMP, nullable=False, autoincrement=True)
    deleted_at: datetime = Column(TIMESTAMP)
    name: str = Column(VARCHAR, nullable=False)
    description: str = Column(VARCHAR)
    group_id: int = Column(Integer, ForeignKey("group_event.id"), nullable=False)
    external_url: int = Column(VARCHAR)
    date_start: date = Column(DATE)
    date_end: date = Column(DATE)
    location: str = Column(String)
    is_cyclically: bool = Column(Boolean)


class UserToEvent(Base):
    __tablename__ = "user_to_event"
    id: int = Column(Integer, primary_key=True)
    created_at: datetime = Column(TIMESTAMP, nullable=False, autoincrement=True)
    update_at: datetime = Column(TIMESTAMP, nullable=False, autoincrement=True)
    deleted_at: datetime = Column(TIMESTAMP)
    user_id: int = Column(Integer, ForeignKey("user.id"), nullable=False)
    event_id: int = Column(Integer, ForeignKey("event.id"), nullable=False)
