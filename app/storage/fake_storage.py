from app.storage import CommitStorage, BranchStorage
from app.models import Commit, Branch
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Dict, Callable, Any, Optional, Tuple, List

import gzip
import pickle

@dataclass
class FakeCommitStorage(CommitStorage):

    data: Dict[str, str] = field(
        default_factory=lambda: FakeCommitStorage.load_if_exists()
    )

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
        self.save_state()
        return commit, None

    def load_if_exists():
        try:
            with open("commits", "rb") as f:
                return pickle.loads(gzip.decompress(f.read()))
        except:
            return {}

    def save_state(self):
        with open("commits", "wb") as f:
            f.write(gzip.compress(pickle.dumps(self.data)))

@dataclass
class FakeBranchStorage(BranchStorage):

    separator: str = "."
    data: Dict[str, str] = field(default_factory=lambda: FakeBranchStorage.load_if_exists())

    @staticmethod
    def construct_id(model_id: str, branch_id: str) -> str:
        return f"{model_id}{FakeBranchStorage.separator}{branch_id}"

    @staticmethod
    def decompose_id(id: str) -> tuple:
        return id.split(FakeBranchStorage.separator)

    def collect(self, search_str: str) -> Tuple[Optional[List[Branch]], Optional[str]]:
        return list(
            map(
                lambda k: Branch.decode(self.data[k]),
                filter(
                    lambda k: search_str in k,
                    self.data,
                )
            )
        ), None
    
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
        self.save_state()
        return (branch, "")

    def load_if_exists():
        try:
            with open("branches", "rb") as f:
                return pickle.loads(gzip.decompress(f.read()))
        except:
            return {}

    def save_state(self):
        with open("branches", "wb") as f:
            f.write(gzip.compress(pickle.dumps(self.data)))
