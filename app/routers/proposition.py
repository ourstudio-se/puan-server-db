from fastapi import APIRouter
from typing import List, Dict
from fastapi import Body

from app.config import ServiceConfiguration
from app.models import Branch, CommitResult, CommitsResult, CommitAssumption, InitResult

router = APIRouter(
    tags=["version control system"],
)

@router.get(
    "/commit/{sha}",
    description="""Gets the commit and its data with hash `sha`"""
)
async def get_commit(sha: str) -> CommitResult:
    return ServiceConfiguration().proposition_service.get_commit(sha)

@router.get(
    "/{model}/{branch}/latest",
    description="""Gets the latest commit on model and branch"""
)
async def commit_latest(model: str, branch: str):
    return ServiceConfiguration().proposition_service.get_commit_latest(model, branch)

@router.get(
    "/{model}/{branch}/commits",
    description="""Gets all commits and their data from model and branch"""
)
async def get_commits(model: str, branch: str) -> CommitsResult:
    return ServiceConfiguration().proposition_service.get_commits(model, branch)

@router.post(
    "/{model}/{branch}/commit",
    description="""Commits new data to model and branch"""
)
async def commit(model: str, branch: str, data: str = Body(...)):
    return ServiceConfiguration().proposition_service.commit(model, branch, data)
