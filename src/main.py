from fastapi import FastAPI
from contextlib import asynccontextmanager

from db import engine
from db import Base
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы в базе данных при старте сервера
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected")
    yield
    await engine.dispose()
    print("Database disconnected")


app = FastAPI(title="MENU", lifespan=lifespan)

app.include_router(router)
