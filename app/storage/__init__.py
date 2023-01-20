
from abc import abstractmethod
from dataclasses import dataclass

from app.models import Commit, Branch
from typing import Optional, Tuple, List

@dataclass
class CommitStorage:

    @abstractmethod
    def retrieve(self, sha: str) -> Tuple[Optional[Commit], Optional[str]]:

        """
            Retrieve commit by key as a sha hash string.
            
            Returns
            -------
            Tuple[Optional[Commit], Optional[str]]
                The left side is the commit if it was found and nothing did go wrong.
                The right side is an error which is None if everything was ok.
        """

        raise NotImplementedError()

    @abstractmethod
    def commit(self, commit: Commit) -> Tuple[Optional[Commit], Optional[str]]:
        """
            Stores a `commit` by creating a sha256 hash from it and returns None if success.
            If there was an error, then that error as a string is returned.
                
            Returns
            -------
            Tuple[Optional[str], Optional[str]]
                The left side is the commit (including sha string), if storing was ok else None.
                The right side is an error, if something went wrong else None.
        """

        raise NotImplementedError()

@dataclass
class BranchStorage:

    @abstractmethod
    def collect(self, search_string: str) -> Tuple[Optional[List[Branch]], Optional[str]]:

        """
            Collects all branches where its key is matching search string.

            Returns
            -------
            Tuple[Optional[List[Branch]], Optional[str]]
                The left side is the list of branches if nothing did go wrong.
                The right side is an error which is None if everything was ok.
        """
        raise NotImplementedError()

    @abstractmethod
    def retrieve(self, model_id: str, branch_id: str) -> Tuple[Optional[Branch], Optional[str]]:

        """
            Retrieve branch from `model_id` and `branch_id`.
            
            Returns
            -------
            Tuple[Optional[Branch], Optional[str]]
                The left side is the branch if it was found and nothing did go wrong.
                The right side is an error which is None if everything was ok.
        """
        raise NotImplementedError()

    @abstractmethod
    def update(self, branch: Branch) -> Tuple[Optional[Branch], Optional[str]]:
        """
            Updates (stores if not exist) a `branch` on it's name. If the name
            is already in db, then the pointer to a commit is updated. 
                
            Returns
            -------
            Tuple[Optional[Branch], Optional[str]]
                The left side is the branch, if updating was ok else None.
                The right side is an error, if something went wrong else None.
        """
        raise NotImplementedError()
