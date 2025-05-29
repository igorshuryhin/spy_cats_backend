from fastapi import FastAPI
from database import engine
from models import Base
from routers import cats
from routers import missions
app = FastAPI()


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(cats.router)
app.include_router(missions.router)