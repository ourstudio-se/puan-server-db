import asyncio

from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

from app.config.settings import Settings
from app.config import ServiceConfiguration
from app.services import PropositionService
from app.storage.fake_storage import FakeBranchStorage, FakeCommitStorage, FakeModelStorage
from app.routers import proposition

app = FastAPI()
app.include_router(proposition.router)

settings = Settings()

@app.get("/healthcheck")
async def healthcheck():
    return "ok"

@app.on_event("startup")
async def startup_event():
    
    # Init shared instances from config
    ServiceConfiguration(
        proposition_service=PropositionService(
            branch_name_default="main",
            branch_storage=FakeBranchStorage(),
            model_storage=FakeModelStorage(),
            commit_storage=FakeCommitStorage()
        ),
    )

config = Config()
config.bind = [settings.app_serve]

if __name__ == '__main__':
    asyncio.run(serve(app, config))