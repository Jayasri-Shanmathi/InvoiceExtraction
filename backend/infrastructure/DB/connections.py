from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from infrastructure.DB.configuration import *
DATABASE_URL=(f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"       
              f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            )

engine=create_async_engine(DATABASE_URL,echo=True,future=True)
AsyncSessionLocal=sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


