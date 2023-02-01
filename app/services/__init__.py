from abc import abstractclassmethod
from app.models import Commit, Branch, CommitResult, InitResult, CommitsResult, CommitAssumption, BranchesResult
from app.storage import  BranchStorage, CommitStorage

from dataclasses import dataclass
from puan import Proposition
from puan.logic.plog import from_b64
from typing import Tuple, Optional, List, Dict
from logging import Logger

@dataclass
class CommitService:

    commit_storage: CommitStorage
    branch_storage: BranchStorage
    logger: Logger

    def validate(self, data: str) -> Optional[str]:

        """
            Returns error if there's one.

            Returns
            -------
            List[str]
        """
        return None

    def commit(self, model_id: str, branch_id: str, data: str) -> CommitResult:

        # Check first that the proposition is fine
        error = self.validate(data)
        if error:
            self.logger.error(error)
            return CommitResult(
                error=f"could not commit for model `{model_id}` and branch `{branch_id}`: validation failed",
            )

        else:

            branch, _ = self.branch_storage.retrieve(model_id, branch_id)

            # Create the commit
            # The branch current commit is parent to this new commit
            commit_new = Commit(
                parent=getattr(
                    branch,
                    "commit_id",
                    None,
                ),
                data=data,
            )
            # Now store the new commit
            commit_stored, error = self.commit_storage.commit(commit_new)
            
            if error:
                self.logger.error(error)
                return CommitResult(
                    error=f"could not commit for model `{model_id}` and branch `{branch_id}`: failed to store",
                )
            
            else:
                # Store/update branch to point to this new commit
                self.branch_storage.update(
                    Branch(
                        id=branch_id,
                        model_id=model_id,
                        commit_id=commit_stored.sha,
                    )
                )

                print(f"commit: `{model_id}` `{branch_id}` `{commit_stored.sha}`")

                return CommitResult(
                    commit=commit_stored,
                    error=error if error is not None else None,
                )
            
    def get_commit(self, commit_sha: str) -> CommitResult:

        """
            Get commit data from commit_sha (hash).

            Returns
            -------
                out: str
        """
        commit, error = self.commit_storage.retrieve(commit_sha)
        if error:
            self.logger.error(error)

        return CommitResult(
            error="could not retreive commit" if error is not None else None,
            commit=commit,
        )

    def get_commits(self, model_id: str, branch_id: str) -> List[Commit]:

        """
            Returns all commits for a model and branch.

            Returns
            -------
                out: List[Commit]
        """
        branch, error = self.branch_storage.retrieve(model_id, branch_id)

        if branch:
            
            first_commit, error = self.commit_storage.retrieve(branch.commit_id)
            if first_commit:

                # Get all other commits from this one
                commits = [first_commit]
                while commits[-1].parent:
                    commit, error = self.commit_storage.retrieve(
                        commits[-1].parent,
                    )
                    if commit:
                        commits.append(commit)
                    else:
                        return CommitResult(
                            error=error
                        )

                return CommitsResult(
                    commits=commits,
                ) 
            else:
                return CommitResult(
                    error=error,
                )

        else:
            return CommitsResult(
                error=error
            )

    def get_commit_latest(self, model_id: str, branch_id: str) -> CommitResult:

        """
            Retrieves the latest commit on model and branch.

            Returns
            -------
                out: CommitResult
        """
        branch, error = self.branch_storage.retrieve(model_id, branch_id)

        if branch:

            commit, error = self.commit_storage.retrieve(branch.commit_id)

            return CommitResult(
                commit=commit,
                error=error,
            )

        else:
            return CommitResult(
                error=error,
            )

    def branches(self, model_id: str) -> BranchesResult:

        """
            Retrieves all branches connecting to `model_id`

            Returns
            -------
            BranchResult
        """

        branches, error = self.branch_storage.collect(model_id)
        return BranchesResult(
            branches=branches,
            error=error,
        )

class PropositionService(CommitService):

    ignore_proposition_validation: bool
    
    def validate(self, data: str) -> Optional[str]:

        if not self.ignore_proposition_validation:
            try:
                proposition = from_b64(data)
            except Exception as e:
                return str(e)

            proposition_errors = proposition.errors()
            if len(proposition_errors) > 0:
                return f"validation error for proposiiton: {proposition_errors}"

        return None

class PolyhedronService(CommitService):

    def decode_data(self, data: str) -> Optional[str]:
        return None