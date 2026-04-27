"""
app/api/auth.py
───────────────
POST /auth/login       → valida access_key única por empresa
GET  /auth/status/{id} → status do plano da empresa
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from datetime import date

from app.core.database import AsyncSessionLocal
from app.models.schema import Company

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    access_key: str   # DEMO-XXXXXX ou FULL-XXXXXX


# ── Helper ────────────────────────────────────────────────────────────────────

def _plan_status(company: Company) -> dict:
    today = date.today()

    if company.plan_expires_at is None:
        return {"is_active": False, "days_remaining": 0}

    exp = company.plan_expires_at
    if isinstance(exp, str):
        exp = date.fromisoformat(exp)

    days_remaining = (exp - today).days
    return {
        "is_active": days_remaining >= 0,
        "days_remaining": max(days_remaining, 0),
    }


# ── Rotas ─────────────────────────────────────────────────────────────────────

@router.post("/auth/login")
async def login(req: LoginRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Company).where(Company.access_key == req.access_key)
        )
        company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=401, detail="Chave de acesso inválida")

    status = _plan_status(company)

    if not status["is_active"]:
        raise HTTPException(
            status_code=403,
            detail="Plano expirado. Entre em contato para renovar."
        )

    exp = company.plan_expires_at
    exp_str = (exp if isinstance(exp, str) else exp.isoformat()) if exp else None

    return {
        "company_id": company.id,
        "company_name": company.name,
        "plan_type": company.plan_type,
        "plan_expires_at": exp_str,
        "is_active": status["is_active"],
        "days_remaining": status["days_remaining"],
    }


@router.get("/auth/status/{company_id}")
async def get_plan_status(company_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Company).where(Company.id == company_id)
        )
        company = result.scalar_one_or_none()

    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    status = _plan_status(company)
    exp = company.plan_expires_at
    exp_str = (exp if isinstance(exp, str) else exp.isoformat()) if exp else None

    return {
        "company_id": company.id,
        "company_name": company.name,
        "plan_type": company.plan_type,
        "plan_expires_at": exp_str,
        "is_active": status["is_active"],
        "days_remaining": status["days_remaining"],
    }