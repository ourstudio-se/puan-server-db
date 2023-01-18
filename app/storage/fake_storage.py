from app.storage import CommitStorage, BranchStorage
from app.models import Commit, Branch, Model
from typing import Dict, Callable, Any, Optional, Tuple

class FakeCommitStorage(CommitStorage):

    data: Dict[str, str] = {}

    def retrieve(self, sha: str) -> Optional[Commit]:
        commit_encoded = self.data.get(sha, None)
        if commit_encoded:
            return Commit.decode(commit_encoded)
        return None

    def commit(self, commit: Commit) -> Optional[str]:
        self.data.setdefault(commit.sha, commit.encode())
        return commit.sha

class FakeBranchStorage(BranchStorage):

    data: Dict[str, str] = {}
    
    def retrieve(self, id: str) -> Optional[Branch]:
        branch_encoded = self.data.get(id, None)
        if branch_encoded:
            return Branch.decode(branch_encoded)
        return None

    def update(self, branch: Branch) -> Tuple[bool, Optional[str]]:
        self.data[branch.id] = branch.encode()
        return (True, "")

class FakeModelStorage(BranchStorage):

    data: Dict[str, str] = {}
    
    def retrieve(self, id: str) -> Optional[Model]:
        model_encoded = self.data.get(id, None)
        if model_encoded:
            return Model.decode(model_encoded)
        return None

    def update(self, model: Branch) -> Tuple[bool, Optional[str]]:
        self.data[model.id] = model.encode()
        return (True, "")