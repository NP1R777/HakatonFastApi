from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.session import get_settings
from src.api import api_router
from src.scheduler.task import check_events_for_notifications


def get_application() -> FastAPI:
    application = FastAPI(root_path=get_settings().root_path)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)

    return application


app = get_application()

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_event():
    scheduler.start()
    scheduler.add_job(
        check_events_for_notifications,
        "cron",
        hour=0,
        minute=0,
    )
# @app.on_event("startup")
# async def startup_event():
#     scheduler.start()
#     scheduler.add_job(
#         check_events_for_notifications,
#         "interval",  # Меняем на interval
#         minutes=1,  # Интервал в одну минуту
#     )


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
