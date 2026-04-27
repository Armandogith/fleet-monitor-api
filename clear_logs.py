import asyncio
from app.core.database import AsyncSessionLocal
from app.models.schema import NotificationLog
from sqlalchemy import delete, func

async def clear():
    async with AsyncSessionLocal() as db:
        result = await db.execute(delete(NotificationLog))
        await db.commit()
        print(f'Todos os logs apagados!')

asyncio.run(clear())