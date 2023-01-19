
from app.models import Commit, Branch, CommitResult, InitResult, CommitsResult, CommitAssumption
from app.storage import  BranchStorage, CommitStorage

from dataclasses import dataclass
from puan import Proposition
from puan.logic.plog import from_b64
from typing import Tuple, Optional, List, Dict

@dataclass
class PropositionService:

    ignore_proposition_validation: bool

    commit_storage: CommitStorage
    branch_storage: BranchStorage

    def decode_data(self, data: str) -> Tuple[Optional[Proposition], Optional[str]]:

        """
            Decodes data string into a Proposition, validates it and returns the proposition and maybe an error string.
        """
        if not self.ignore_proposition_validation:
            try:
                proposition = from_b64(data)
            except Exception as e:
                return str(e)

            proposition_errors = proposition.errors()
            if len(proposition_errors) > 0:
                return f"validation error for proposiiton: {proposition_errors}"

        return None

    def commit(self, model_id: str, branch_id: str, data: str) -> CommitResult:

        # Check first that the proposition is fine
        error = self.decode_data(data)
        if error:

            return CommitResult(error=error)

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

                return CommitResult(
                    error=error,
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
        return CommitResult(
            error=error if error is not None else None,
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