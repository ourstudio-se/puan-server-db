from hashlib import sha256
from app.storage import CommitStorage, BranchStorage
from app.models import Commit, Branch
from typing import Dict, Callable, Any, Optional, Tuple

class FakeCommitStorage(CommitStorage):

    data: Dict[str, str] = {}

    @staticmethod
    def hash(commit: Commit, str_encoding: str = 'utf8') -> str:
        return sha256(commit.data.encode(str_encoding)).hexdigest()

    def retrieve(self, sha: str) -> Tuple[Optional[Commit], Optional[str]]:
        commit_encoded = self.data.get(sha, None)
        if commit_encoded:
            return (Commit.decode(commit_encoded), None)
        return (None, f"commit with sha '{sha}' was not found")

    def commit(self, commit: Commit) -> Tuple[Optional[Commit], Optional[str]]:
        commit.sha = self.hash(commit)
        _commit, _ = self.retrieve(commit.sha)
        if _commit:
            return _commit, None
            
        self.data.setdefault(commit.sha, commit.encode())
        return commit, None

class FakeBranchStorage(BranchStorage):

    data: Dict[str, str] = {}

    @staticmethod
    def construct_id(model_id: str, branch_id: str) -> str:
        return f"{model_id}.{branch_id}"
    
    def retrieve(self, model_id: str, branch_id: str) -> Tuple[Optional[Branch], Optional[str]]:
        branch_encoded = self.data.get(
            self.construct_id(model_id, branch_id), 
            None,
        )
        if branch_encoded:
            return (Branch.decode(branch_encoded), None)
        return (None, f"could not find branch with model id '{model_id}' and branch id '{branch_id}'")

    def update(self, branch: Branch) -> Tuple[Optional[Branch], Optional[str]]:
        self.data[self.construct_id(branch.model_id, branch.id)] = branch.encode()
        return (branch, "")
