
from abc import abstractmethod
from dataclasses import dataclass

from app.models import Commit, Branch, Model
from typing import Optional, Tuple

@dataclass
class CommitStorage:

    @abstractmethod
    def retrieve(self, sha: str) -> Optional[Commit]:

        """
            Retrieve commit by key as a sha hash string.
            
            Returns
            -------
            Optional[Commit]
        """

        raise NotImplementedError()

    @abstractmethod
    def commit(self, commit: Commit) -> Optional[str]:
        """
            Stores a `commit` by creating a sha256 hash from it and returns that value
            if store was a success.
                
            Returns
            -------
            Optional[str]
        """

        raise NotImplementedError()

@dataclass
class BranchStorage:

    @abstractmethod
    def retrieve(self, id: str) -> Optional[Branch]:

        """
            Retrieve branch by key as a `id` string.
            
            Returns
            -------
            Optional[Branch]
        """

        raise NotImplementedError()

    @abstractmethod
    def update(self, branch: Branch) -> Tuple[bool, Optional[str]]:
        """
            Updates (stores if not exist) a `branch` on it's name. If the name
            is already in db, then the pointer to a commit is updated. 
                
            Returns
            -------
            Tuple[bool, Optional[str]]
                A bool indicating success or not. A message is sent back as second parameter
                to give more information of what went wrong. If True and a message is set, the
                message indicate a warning.
        """

        raise NotImplementedError()

@dataclass
class ModelStorage:

    @abstractmethod
    def retrieve(self, id: str) -> Optional[Model]:

        """
            Retrieves a model by id. If no model by that id,
            None is returned.

            Returns
            -------
            Optional[Model]
        """
        raise NotImplementedError()

    @abstractmethod
    def update(self, model: Model) -> Tuple[bool, Optional[str]]:

        """
            Updates (stores if not exist) a `branch` on it's name. If the name
            is already in db, then the pointer to a commit is updated. 
                
            Returns
            -------
            Tuple[bool, Optional[str]]
                A bool indicating success or not. A message is sent back as second parameter
                to give more information of what went wrong. If True and a message is set, the
                message indicate a warning.
        """
        raise NotImplementedError()