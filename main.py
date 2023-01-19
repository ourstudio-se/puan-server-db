import asyncio
import logging
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from hypercorn.asyncio import serve
from hypercorn.config import Config

from app.config.settings import Settings
from app.config import ServiceConfiguration
from app.services import PropositionService
from app.storage.fake_storage import FakeBranchStorage, FakeCommitStorage
from app.routers import proposition

app = FastAPI()
app.include_router(proposition.router)

settings = Settings()
logger = logging.getLogger(settings.app_name)

@app.get("/healthcheck")
async def healthcheck():
    return "ok"

@app.on_event("startup")
async def startup_event():
    
    # Init shared instances from config
    ServiceConfiguration(
        proposition_service=PropositionService(
            ignore_proposition_validation=settings.ignore_proposition_validation,
            branch_storage=FakeBranchStorage(),
            commit_storage=FakeCommitStorage()
        ),
    )

@app.middleware("http")
async def error_logging_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        correlation_id = request.headers.get("x-correlation-id", None)
        logger.error(
            json.dumps(
                {
                    "app": settings.app_name,
                    "level": "error",
                    "@timestamp": str(datetime.now()).replace(" ", "T")[:-2],
                    "correlation_id": correlation_id,
                    "message": str(e),
                }
            )
        )
        return JSONResponse(
            status_code=500, 
            content="We are sorry but something went terribly wrong...",
        )

config = Config()
config.bind = [settings.app_serve]

if __name__ == '__main__':
    asyncio.run(serve(app, config))