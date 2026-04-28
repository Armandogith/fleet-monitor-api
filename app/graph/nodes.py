from datetime import date, timedelta
from sqlalchemy import select
from app.models.schema import Document, Driver, NotificationLog, Company
from app.core.database import AsyncSessionLocal
from app.services.sms import sms_service
from app.services.email import email_service
import uuid

def get_days_remaining(exp_date):
    return (exp_date - date.today()).days

async def fetch_expiring_docs(state):
    today = date.today()
    limit_date = today + timedelta(days=30)

    async with AsyncSessionLocal() as session:
        logs_hoje = await session.execute(
            select(NotificationLog.document_id)
            .where(NotificationLog.status == "success")
            .where(NotificationLog.timestamp >= today)
        )
        ids_ja_notificados = set(row[0] for row in logs_hoje.all())

        query = (
            select(Document, Driver, Company)
            .join(Driver, Document.driver_id == Driver.id)
            .join(Company, Driver.company_id == Company.id)
            .where(Document.expiration_date >= today)
            .where(Document.expiration_date <= limit_date)
        )
        result = await session.execute(query)
        rows = result.all()

        pending_tasks = []
        for doc, driver, company in rows:
            if doc.id in ids_ja_notificados:
                print(f"⏭️ Pulando doc #{doc.id} ({driver.name}) — já notificado hoje")
                continue
            days = get_days_remaining(doc.expiration_date)
            pending_tasks.append({
                "document_id": doc.id,
                "driver_name": driver.name,
                "phone": driver.phone_number,
                "doc_type": doc.doc_type,
                "days_remaining": days,
                "responsible_email": company.responsible_email,
            })

    print(f"📋 {len(pending_tasks)} documentos para notificar ({len(ids_ja_notificados)} já notificados hoje)")
    return {"batch_id": str(uuid.uuid4()), "pending_tasks": pending_tasks}

async def send_sms_alert(state):
    task = state.get("task", state)
    result = {
        "document_id": task["document_id"],
        "driver_name": task["driver_name"],
        "status": "success",
        "error": ""
    }
    try:
        await sms_service.send_alert(
            phone=task["phone"],
            driver_name=task["driver_name"],
            doc_type=task["doc_type"],
            days_remaining=task["days_remaining"]
        )
        if task["days_remaining"] <= 7 and task.get("responsible_email"):
            try:
                await email_service.send_alert(
                    to_email=task["responsible_email"],
                    driver_name=task["driver_name"],
                    doc_type=task["doc_type"],
                    days_remaining=task["days_remaining"]
                )
                print(f"📧 Email enviado para {task['responsible_email']}")
            except Exception as e:
                print(f"❌ Erro email: {e}")
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"❌ Erro SMS para {task['driver_name']}: {e}")
    # Salva log diretamente no banco
    async with AsyncSessionLocal() as session:
        log = NotificationLog(
            document_id=result.get("document_id"),
            status=result.get("status", "error"),
            error_message=result.get("error", "")
        )
        session.add(log)
        await session.commit()
        print(f"✅ Log salvo: {task['driver_name']} - {result['status']}")
    return result

async def persist_and_cleanup(state):
    send_results = state.get("send_results", [])
    if not send_results:
        return state
    async with AsyncSessionLocal() as session:
        for r in send_results:
            if not isinstance(r, dict):
                continue
            log = NotificationLog(
                document_id=r.get("document_id"),
                status=r.get("status", "error"),
                error_message=r.get("error", "")
            )
            session.add(log)
        await session.commit()
    print(f"✅ {len(send_results)} logs salvos no banco")
    return state