from datetime import date, timedelta
from sqlalchemy import select
from app.models.schema import Document, Driver, NotificationLog
from app.core.database import AsyncSessionLocal
from app.services.whatsapp import whatsapp_service
import uuid

async def fetch_expiring_docs(state):
    today = date.today()
    # Prazos de aviso: 30 dias, 15 dias e 7 dias antes do vencimento
    target_dates = [today + timedelta(days=d) for d in [7, 15, 30]]
    days_map = {(today + timedelta(days=d)): d for d in [7, 15, 30]}

    async with AsyncSessionLocal() as session:
        query = select(Document, Driver).join(Driver).where(Document.expiration_date.in_(target_dates))
        result = await session.execute(query)
        rows = result.all()

        pending_tasks = []
        for doc, driver in rows:
            pending_tasks.append({
                "document_id": doc.id,
                "driver_name": driver.name,
                "phone": driver.phone_number,
                "doc_type": doc.doc_type,
                "days_remaining": days_map[doc.expiration_date],
            })

    return {"batch_id": str(uuid.uuid4()), "pending_tasks": pending_tasks}

async def send_whatsapp_alert(state):
    task = state.get("task", state)
    result = {
        "document_id": task["document_id"],
        "driver_name": task["driver_name"],
        "status": "success",
        "error": ""
    }
    try:
        # Chama a API real da Meta (configurada no arquivo whatsapp.py)
        await whatsapp_service.send_alert(
            phone=task["phone"],
            driver_name=task["driver_name"],
            doc_type=task["doc_type"],
            days_remaining=task["days_remaining"]
        )
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        
    return {"send_results": [result]}

async def persist_and_cleanup(state):
    results = state.get("send_results", [])
    if results:
        async with AsyncSessionLocal() as session:
            logs = [NotificationLog(
                document_id=res["document_id"], 
                status=res["status"], 
                error_message=res["error"] or None
            ) for res in results]
            session.add_all(logs)
            await session.commit()
            
    print(f"✅ Lote processado: {len(results)} alertas | Sucesso: {sum(1 for r in results if r['status']=='success')}")
    return {"pending_tasks": [], "send_results": []}