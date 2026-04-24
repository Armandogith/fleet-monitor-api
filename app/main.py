from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router
from app.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o banco de dados ao ligar o servidor
    await init_db()
    print("🚀 Servidor Monitor de Frota Iniciado com Sucesso!")
    yield

app = FastAPI(
    title="Transport Monitor API",
    description="API para gestão de validade de documentos de motoristas",
    version="1.0.0",
    lifespan=lifespan
)

# Adiciona as rotas que criamos no endpoints.py
app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "API de Monitoramento de Frota operando normalmente."}