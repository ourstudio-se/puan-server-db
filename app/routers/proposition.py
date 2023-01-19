from fastapi import APIRouter
from typing import List, Dict
from fastapi import Body

from app.config import ServiceConfiguration
from app.models import Model, Branch, ModelInit, CommitResult, CommitsResult, CommitAssumption, InitResult

router = APIRouter(
    tags=["version control system"],
)

@router.post(
    "/model/init",
    description="""Starting point for a new model. Creates a new model with default branch 'main'."""
)
async def model_create(model: ModelInit = Body(...)) -> InitResult:
    return ServiceConfiguration().proposition_service.init(model.id, model.name, model.author, model.data)


@router.get(
    "/commit/{sha}",
    description="""Gets the commit and its data with hash `sha`"""
)
async def get_commit(sha: str) -> CommitResult:
    return ServiceConfiguration().proposition_service.get_commit(sha)

@router.post(
    "/commit/assume/{sha}",
    description="""Assumes something about the data on commit with hash `sha` and returns the consequence. The input body is a dict with variable ids as keys and the assumed values (ints) as keys."""
)
async def commit_assume(sha: str, assumption: Dict[str, int] = Body(...)) -> CommitAssumption:
    return ServiceConfiguration().proposition_service.assume_commit(sha, assumption)

@router.get(
    "/{model}/{branch}/latest",
    description="""Gets the latest commit on model and branch"""
)
async def commit_latest(model: str, branch: str):
    return ServiceConfiguration().proposition_service.commit_latest(model, branch)

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

@router.post(
    "/{model}/{branch}/branch",
    description="""Creates a new branch with name `name`, branching from given model and branch."""
)
async def branching(model: str, branch: str, name: str) -> InitResult:
    return ServiceConfiguration().proposition_service.branching(model, branch, name)
