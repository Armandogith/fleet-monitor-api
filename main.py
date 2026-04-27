from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import router
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.core.database import init_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_daily_job():
    try:
        logger.info("🔄 Iniciando job diário...")
        from app.graph.workflow import create_workflow
        workflow = create_workflow()
        result = await workflow.ainvoke({
            "batch_id": "",
            "pending_tasks": [],
            "send_results": [],
        })
        total = len(result.get("send_results", []))
        logger.info(f"✅ Job diário concluído: {total} notificações enviadas")
    except Exception as e:
        logger.error(f"❌ Erro no job diário: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler.add_job(run_daily_job, "cron", hour=8, minute=0, id="daily_job")
    scheduler.start()
    logger.info("✅ Servidor iniciado! Job diário às 08:00")
    yield
    scheduler.shutdown()


app = FastAPI(title="Transport Monitor API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)
app.include_router(admin_router)

app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/")
async def root():
    return {"message": "Transport Monitor API v2.0 rodando!"}


@app.post("/trigger-scheduler")
async def trigger_scheduler():
    try:
        await run_daily_job()
        return {"message": "Job executado com sucesso!"}
    except Exception as e:
        return {"error": str(e)}