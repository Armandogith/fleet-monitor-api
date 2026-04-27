import asyncio
from app.core.database import AsyncSessionLocal
from app.models.schema import Driver, Document
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        drivers = await db.execute(select(Driver))
        for d in drivers.scalars():
            print(f'Motorista: {d.name} | Tel: {d.phone_number} | ID: {d.id}')
        docs = await db.execute(select(Document))
        for doc in docs.scalars():
            print(f'Doc: {doc.doc_type} | Vence: {doc.expiration_date} | Driver ID: {doc.driver_id}')

asyncio.run(check())