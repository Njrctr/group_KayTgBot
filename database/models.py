from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    BigInteger, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database_build import Base


class UsersOrm(Base):
    __tablename__ = "users"
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    username: Mapped[Optional[str]]
    name: Mapped[Optional[str]]

    nickname: Mapped[Optional[str]]
    msg_count: Mapped[int] = mapped_column(default=0)
    symbol_count: Mapped[int] = mapped_column(default=0)
    last_message: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.now
    )
    fun_answer: Mapped[Optional[str]]
    fun_answer_date: Mapped[Optional[date]]


class BannedStickersOrm(Base):
    __tablename__ = "baned_stickers"
    id: Mapped[int] = mapped_column(primary_key=True)
    set_name: Mapped[str]


class FunAnswersOrm(Base):
    __tablename__ = "funs"
    id: Mapped[int] = mapped_column(primary_key=True)
    answer: Mapped[str]
