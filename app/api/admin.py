"""
app/api/admin.py
────────────────
Rotas exclusivas do dono do sistema (sem autenticação de cliente).

GET  /admin/companies              → lista todas as empresas com status
POST /admin/companies              → cria nova empresa
POST /admin/generate-key/{id}      → gera nova senha (demo 7d ou full 30d)
DELETE /admin/companies/{id}       → remove empresa
GET  /admin/stats                  → totais gerais
"""

import random
import string
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from datetime import date, timedelta
from typing import Optional

from app.core.database import AsyncSessionLocal
from app.models.schema import Company, Driver, Document, NotificationLog

router = APIRouter(prefix="/admin", tags=["admin"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _generate_key(plan_type: str) -> str:
    """Gera senha única estilo DEMO-A3K9 / FULL-X7M2"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    prefix = "DEMO" if plan_type == "demo" else "FULL"
    return f"{prefix}-{suffix}"


def _plan_status(company: Company) -> dict:
    today = date.today()
    if company.plan_expires_at is None:
        return {"is_active": False, "days_remaining": 0, "status_label": "Sem plano"}

    exp = company.plan_expires_at
    if isinstance(exp, str):
        exp = date.fromisoformat(exp)

    days_remaining = (exp - today).days
    is_active = days_remaining >= 0

    if not is_active:
        label = "Expirado"
    elif days_remaining <= 2:
        label = "Crítico"
    elif days_remaining <= 7:
        label = "Atenção"
    else:
        label = "Ativo"

    return {
        "is_active": is_active,
        "days_remaining": max(days_remaining, 0),
        "status_label": label,
    }


def _company_dict(company: Company, driver_count: int = 0) -> dict:
    status = _plan_status(company)
    exp = company.plan_expires_at
    exp_str = (exp if isinstance(exp, str) else exp.isoformat()) if exp else None
    return {
        "id": company.id,
        "name": company.name,
        "responsible_email": company.responsible_email,
        "responsible_whatsapp": company.responsible_whatsapp,
        "plan_type": company.plan_type,
        "plan_expires_at": exp_str,
        "access_key": company.access_key,
        "driver_count": driver_count,
        **status,
    }


# ── Schemas ───────────────────────────────────────────────────────────────────

class CreateCompanyRequest(BaseModel):
    name: str
    responsible_email: Optional[str] = None
    responsible_whatsapp: Optional[str] = None
    plan_type: str = "demo"   # "demo" | "full"


class GenerateKeyRequest(BaseModel):
    plan_type: str   # "demo" | "full"


# ── Rotas ─────────────────────────────────────────────────────────────────────

@router.get("/companies")
async def list_companies():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Company).order_by(Company.id.desc()))
        companies = result.scalars().all()

        # Contar motoristas por empresa
        driver_counts = {}
        for c in companies:
            count_result = await session.execute(
                select(func.count(Driver.id)).where(Driver.company_id == c.id)
            )
            driver_counts[c.id] = count_result.scalar() or 0

    return [_company_dict(c, driver_counts.get(c.id, 0)) for c in companies]


@router.post("/companies")
async def create_company(req: CreateCompanyRequest):
    if req.plan_type not in ("demo", "full"):
        raise HTTPException(status_code=400, detail="plan_type deve ser 'demo' ou 'full'")

    today = date.today()
    expires = today + timedelta(days=7 if req.plan_type == "demo" else 30)

    # Gera chave única — tenta até não colidir
    async with AsyncSessionLocal() as session:
        for _ in range(10):
            key = _generate_key(req.plan_type)
            existing = await session.execute(
                select(Company).where(Company.access_key == key)
            )
            if not existing.scalar_one_or_none():
                break

        company = Company(
            name=req.name,
            responsible_email=req.responsible_email,
            responsible_whatsapp=req.responsible_whatsapp,
            plan_type=req.plan_type,
            plan_expires_at=expires,
            access_key=key,
        )
        session.add(company)
        await session.commit()
        await session.refresh(company)

    return {
        "message": f"Empresa '{company.name}' criada com sucesso!",
        "company": _company_dict(company),
    }


@router.post("/generate-key/{company_id}")
async def generate_new_key(company_id: int, req: GenerateKeyRequest):
    if req.plan_type not in ("demo", "full"):
        raise HTTPException(status_code=400, detail="plan_type deve ser 'demo' ou 'full'")

    today = date.today()
    expires = today + timedelta(days=7 if req.plan_type == "demo" else 30)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()

        if not company:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        # Gera nova chave única
        for _ in range(10):
            key = _generate_key(req.plan_type)
            existing = await session.execute(
                select(Company).where(Company.access_key == key)
            )
            if not existing.scalar_one_or_none():
                break

        company.access_key = key
        company.plan_type = req.plan_type
        company.plan_expires_at = expires
        await session.commit()
        await session.refresh(company)

    return {
        "message": f"Nova chave gerada para '{company.name}'",
        "access_key": key,
        "plan_type": req.plan_type,
        "plan_expires_at": expires.isoformat(),
    }


@router.delete("/companies/{company_id}")
async def delete_company(company_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()

        if not company:
            raise HTTPException(status_code=404, detail="Empresa não encontrada")

        name = company.name
        await session.delete(company)
        await session.commit()

    return {"message": f"Empresa '{name}' removida com sucesso"}


@router.get("/stats")
async def get_stats():
    async with AsyncSessionLocal() as session:
        total_companies = (await session.execute(select(func.count(Company.id)))).scalar()
        total_drivers = (await session.execute(select(func.count(Driver.id)))).scalar()
        total_docs = (await session.execute(select(func.count(Document.id)))).scalar()
        total_logs = (await session.execute(select(func.count(NotificationLog.id)))).scalar()

        # Empresas ativas
        today = date.today()
        active_result = await session.execute(
            select(func.count(Company.id)).where(
                Company.plan_expires_at >= today
            )
        )
        active_companies = active_result.scalar()

        # Planos demo vs full
        demo_result = await session.execute(
            select(func.count(Company.id)).where(Company.plan_type == "demo")
        )
        full_result = await session.execute(
            select(func.count(Company.id)).where(Company.plan_type == "full")
        )

    return {
        "total_companies": total_companies,
        "active_companies": active_companies,
        "demo_plans": demo_result.scalar(),
        "full_plans": full_result.scalar(),
        "total_drivers": total_drivers,
        "total_documents": total_docs,
        "total_notifications_sent": total_logs,
    }