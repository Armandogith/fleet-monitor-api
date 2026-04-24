from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.schema import Driver, Document

router = APIRouter()

# --- MODELOS DE ENTRADA (INPUT MANUAL) ---
class DriverCreate(BaseModel):
    company_id: int
    name: str
    phone_number: str

class DocumentCreate(BaseModel):
    driver_id: int
    doc_type: str
    expiration_date: date

# Dependência do banco
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- ROTAS DE INPUT MANUAL ---
@router.post("/drivers")
async def create_driver(driver: DriverCreate, db: AsyncSession = Depends(get_db)):
    new_driver = Driver(company_id=driver.company_id, name=driver.name, phone_number=driver.phone_number)
    db.add(new_driver)
    await db.commit()
    return {"status": "success", "driver_id": new_driver.id}

@router.post("/documents")
async def create_document(doc: DocumentCreate, db: AsyncSession = Depends(get_db)):
    new_doc = Document(driver_id=doc.driver_id, doc_type=doc.doc_type, expiration_date=doc.expiration_date)
    db.add(new_doc)
    await db.commit()
    return {"status": "success", "document_id": new_doc.id}

# --- ROTA QUE DISPARA O JOB DIÁRIO ---
@router.post("/trigger-job")
async def trigger_job():
    from app.graph.workflow import create_workflow
    workflow = create_workflow()
    result = await workflow.ainvoke({"batch_id": "", "pending_tasks": [], "send_results": []})
    return {"status": "ok", "notificacoes_enviadas": len(result.get("send_results", []))}