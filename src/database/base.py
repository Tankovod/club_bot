from sqlalchemy import Column, INT
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.types.settings import settings


class Base(DeclarativeBase):
    async_engine = create_async_engine(url=settings.DATABASE_URL.unicode_string())
    session = async_sessionmaker(bind=async_engine)

    id = Column(INT, primary_key=True)
