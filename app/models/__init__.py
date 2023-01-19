from hashlib import sha256
from pydantic import BaseModel
from typing import Optional, List

import pickle
import gzip
import base64

class Picklable(BaseModel):

    def encode(self, str_encoding: str = 'utf8') -> str:
        return base64.b64encode(
            gzip.compress(
                pickle.dumps(
                    self,
                    protocol=pickle.HIGHEST_PROTOCOL,
                ),
                mtime=0,
            )
        ).decode(str_encoding)

    @staticmethod
    def decode(encoded: str) -> "Picklable":
        return pickle.loads(
            gzip.decompress(
                base64.b64decode(
                    encoded.encode()
                )
            )
        )

class Commit(Picklable):

    sha:    Optional[str] = None
    parent: Optional[str] = None
    author: str = ""
    data:   str

    def hash(self, str_encoding: str = 'utf8') -> str:
        return sha256(self.data.encode(str_encoding)).hexdigest()

class Branch(Picklable):

    name:       str
    commit_id:  str
    model_id:   str

    @property
    def id(self):
        return Branch._construct_id(self.model_id, self.name)

    @staticmethod
    def _construct_id(model_id: str, name: str) -> str:
        return f"{model_id}.{name}"

class Model(Picklable):

    id: str
    name: str
    branches: List[str] = []

class ModelInit(BaseModel):

    id: str
    name: str
    author: str = ""
    data: str

class InitResult(BaseModel):

    error:  Optional[str] = None
    model:  Optional[str] = None
    branch: Optional[str] = None


class CommitResult(BaseModel):

    error:  Optional[str] = None
    commit: Optional[Commit] = None

class CommitsResult(BaseModel):

    commits: Optional[List[Commit]] = None
    error:   Optional[str] = None

class CommitProposition(BaseModel):

    author: str
    proposition_compressed: str

class CommitAssumption(BaseModel):

    data:  Optional[str] = None
    error: Optional[str] = None
