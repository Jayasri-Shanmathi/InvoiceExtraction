import asyncio
from backend.infrastructure.DB.connections import engine
from backend.infrastructure.DB.models import Base

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())
