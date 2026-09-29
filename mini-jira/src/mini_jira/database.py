from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = "sqlite+aiosqlite:///./app.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker[AsyncSession](engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session