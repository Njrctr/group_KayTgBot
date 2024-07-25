from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config.configuration import config


async_engine = create_async_engine(
    url=config.POSTGRES_URL,
    echo=False,
)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    
    def __repr__(self) -> str:
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {", ".join(cols)}>"
