
from app.models import Commit, Branch, CommitResult, Model, ModelInit, ModelInitResult, CommitsResult
from app.storage import ModelStorage, BranchStorage, CommitStorage

from dataclasses import dataclass
from puan import Proposition
from typing import Tuple, Optional, List
from itertools import takewhile

@dataclass
class PropositionService:

    branch_name_default: str

    commit_storage: CommitStorage
    branch_storage: BranchStorage
    model_storage:  ModelStorage

    @staticmethod
    def validate_proposition(proposition: Proposition) -> Optional[str]:

        """
            Will return a error as a string if the proposition was invalid
        """
        proposition_errors = proposition.errors()
        if len(proposition_errors) > 0:
            return f"validation error for proposiiton: {proposition_errors}"

        return None

    def commit(self, model_id: str, branch_name: str, proposition: Proposition) -> CommitResult:

        # Check first that the proposition is fine
        error = self.validate_proposition(proposition)
        if error:
            return CommitResult(error=error)

        else:

            # Get current commit for branch
            branch = self.branch_storage.retrieve(
                # construct the branch id
                Branch._construct_id(model_id, branch_name)
            )
            
            if branch is not None:

                # Create the commit
                # The branch current commit is parent to this new commit
                commit = Commit(
                    parent=branch.commit_id,
                    author=author,
                    data=proposition.to_b64(),
                )
                commit.sha = commit.hash()

                # If there was no change from parent, then
                # just return the same commit
                if commit.sha == branch.commit_id:
                    return CommitResult(
                        error="no change was committed",
                        commit=commit,
                        data=commit.data
                    )

                else:

                    # Now store the new commit
                    sha = self.commit_storage.commit(commit)
                        
                    # Update the branch to point to this new commit
                    branch.commit_id = sha
                    self.branch_storage.update(branch)

                    return CommitResult(
                        commit=commit,
                        error="could not store commit :( sowy." if sha is None else None,
                    )
            else:

                return CommitResult(
                    error="model and/or branch does not exists",
                )

    def init(self, model_id: str, model_name: str, author: str, proposition: Proposition) -> ModelInitResult:
        
        # Check first that the proposition is fine
        error = self.validate_proposition(proposition)
        if error:
            return CommitResult(error=error)

        else:

            # Check that the model does not exists
            if self.model_storage.retrieve(model_id) is None:

                # create commit for it with data from init
                commit = Commit(
                    author=author,
                    data=proposition.to_b64(),
                )
                commit.sha = commit.hash()

                # and store it
                sha = self.commit_storage.commit(commit)

                if sha is not None:

                    success, error = self.model_storage.update(
                        Model(
                            id=model_id, 
                            name=model_name,
                            branches=[self.branch_name_default],
                        )
                    )

                    if success:
                        
                        success, error = self.branch_storage.update(
                            Branch(
                                name=self.branch_name_default,
                                commit_id=sha,
                                model_id=model_id,
                            )
                        )

                        return ModelInitResult(
                            error=f"could not store branch: {error}" if not success else None
                        )

                    else:
                        return ModelInitResult(
                            error=f"could not store model: {error}"
                        )

                else:

                    return ModelInitResult(
                        error="could not store initial commit :("
                    )

            else:
                return ModelInitResult(
                    error=f"model with id '{model_id}' already exist"
                )

    def get_commit(self, commit_sha: str) -> CommitResult:

        """
            Get commit data from commit_sha (hash).

            Returns
            -------
                out: str
        """
        commit = self.commit_storage.retrieve(commit_sha)

        return CommitResult(
            error=f"could not find data for commit '{commit_sha}'" if commit is None else None,
            commit=commit,
            data=commit.data,
        )

    def get_commits(self, model_id: str, branch_name: str) -> List[Commit]:

        """
            Returns all commits for a model and branch.

            Returns
            -------
                out: List[Commit]
        """
        branch = self.branch_storage.retrieve(
            Branch._construct_id(model_id, branch_name)
        )

        if branch:

            commits = [self.commit_storage.retrieve(branch.commit_id)]

            while commits[-1].parent:
                commits.append(
                    self.commit_storage.retrieve(
                        commits[-1].parent,
                    )
                )

            return CommitsResult(
                commits=commits,
            ) 

        else:
            return CommitsResult(
                error=f"could not find branch '{branch_name}' for model with id '{model}'"
            )