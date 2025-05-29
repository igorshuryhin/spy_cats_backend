from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    session = async_session()
    try:
        yield session
    finally:
        await session.close()
