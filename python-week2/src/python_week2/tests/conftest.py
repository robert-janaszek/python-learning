import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from python_week2.main import app
from python_week2.database import get_db
from python_week2.models import Base
from python_week2.tests.database import engine, get_db_memory

@pytest_asyncio.fixture
async def async_client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_db] = get_db_memory
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
