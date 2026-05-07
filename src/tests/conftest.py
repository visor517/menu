import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

from db import AsyncSessionLocal
from main import app


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db():
    """Очищает все таблицы перед каждым тестом"""
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM dishes"))
        await session.execute(text("DELETE FROM sub_menus"))
        await session.execute(text("DELETE FROM menus"))
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Создает асинхронный HTTP-клиент"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
