from fastapi import APIRouter
from typing import List
from fastapi import Body
from puan.logic.plog import from_b64

from app.config import ServiceConfiguration
from app.models import Model, Branch, ModelInit, CommitResult, CommitsResult

router = APIRouter(
    tags=["proposition"],
)

@router.get("/commit/{sha}")
async def get_commit(sha: str) -> CommitResult:
    return ServiceConfiguration().proposition_service.get_commit(sha)

@router.get("/{model}/{branch}/commits")
async def get_commits(model: str, branch: str) -> CommitsResult:
    return ServiceConfiguration().proposition_service.get_commits(model, branch)

@router.post("/{model}/{branch}/commit")
async def commit(model: str, branch: str, proposition: str = Body(...)):
    return ServiceConfiguration().proposition_service.commit(model, branch, from_b64(proposition))

@router.post("/model/init")
async def model_create(model: ModelInit = Body(...)):
    return ServiceConfiguration().proposition_service.init(model.id, model.name, model.author, from_b64(model.proposition))
