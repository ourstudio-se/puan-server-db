
from app.models import Commit, Branch, CommitResult, Model, ModelInit, InitResult, CommitsResult, CommitAssumption
from app.storage import ModelStorage, BranchStorage, CommitStorage

from dataclasses import dataclass
from puan import Proposition
from puan.logic.plog import from_b64
from typing import Tuple, Optional, List, Dict
from itertools import takewhile

@dataclass
class PropositionService:

    branch_name_default: str
    ignore_proposition_validation: bool

    commit_storage: CommitStorage
    branch_storage: BranchStorage
    model_storage:  ModelStorage

    def decode_data(self, data: str) -> Tuple[Optional[Proposition], Optional[str]]:

        """
            Decodes data string into a Proposition, validates it and returns the proposition and maybe an error string.
        """
        try:
            proposition = from_b64(data)
        except Exception as e:
            return None, str(e)

        if not self.ignore_proposition_validation:
            proposition_errors = proposition.errors()
            if len(proposition_errors) > 0:
                return None, f"validation error for proposiiton: {proposition_errors}"

        return proposition, None

    def commit(self, model_id: str, branch_name: str, data: str) -> CommitResult:

        # Check first that the proposition is fine
        proposition, error = self.decode_data(data)
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

    def init(self, model_id: str, model_name: str, author: str, data: str) -> InitResult:

        """
            Init a model with default branch name and commits the given proposition as a starting point.

            Returns
            -------
                out: InitResult
        """
        
        # Check first that the proposition is fine
        proposition, error = self.decode_data(data)
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

                    model = Model(
                        id=model_id, 
                        name=model_name,
                        branches=[self.branch_name_default],
                    )
                    success, error = self.model_storage.update(model)

                    if success:
                        
                        branch = Branch(
                            name=self.branch_name_default,
                            commit_id=sha,
                            model_id=model.id,
                        )
                        success, error = self.branch_storage.update(branch)

                        return InitResult(
                            error=f"could not store branch: {error}" if not success else None,
                            model=model.id if success else None,
                            branch=branch.name,
                        )

                    else:
                        return InitResult(
                            error=f"could not store model: {error}"
                        )

                else:

                    return InitResult(
                        error="could not store initial commit :("
                    )

            else:
                return InitResult(
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
                error=f"could not find branch '{branch_name}' for model with id '{model_id}'"
            )

    def assume_commit(self, commit_sha: str, assumption: Dict[str, int]) -> CommitAssumption:

        """
            Assumes `assumption` on data from commit. Returns assumed data.

            Returns
            -------
                out: CommitAssumption
        """

        commit = self.commit_storage.retrieve(commit_sha)

        if commit:
            
            # unpack data and assume
            try:
                proposition = from_b64(commit.data)
            except Exception as e:
                return CommitAssumption(
                    error=f"could not unpack data from commit: {e}"
                )

            try:
                assumed = proposition.assume(assumption)
            except Exception as e:
                return CommitAssumption(
                    error=f"could not assume `assumption` on commit's data: {e}"
                )

            return CommitAssumption(
                data=assumed.to_b64(),
            )

        else:
            return CommitAssumption(
                error=f"could not find commit with sha '{commit_sha}'"
            )

    def branching(self, model_id: str, on_branch_name: str, new_branch_name: str) -> InitResult:

        """
            Creates a new branch `new_branch_name` pointing initially at same commit
            as branch `on_branch_name`.

            Returns
            -------
                out: InitResult
        """
        branch = self.branch_storage.retrieve(
            Branch._construct_id(model_id, on_branch_name),
        )

        if branch:

            new_branch = Branch(
                model_id=model_id,
                commit_id=branch.commit_id,
                name=new_branch_name, 
            )

            success, error = self.branch_storage.update(new_branch)

            return InitResult(
                error=None if success else error,
                branch=new_branch.name,
                model=model_id,
            )

        else:
            return InitResult(
                error=f"could not find branch '{on_branch_name}' in model '{model_id}'"
            )

    def commit_latest(self, model_id: str, branch_name: str) -> CommitResult:

        """
            Retrieves the latest commit on model and branch.

            Returns
            -------
                out: CommitResult
        """
        branch = self.branch_storage.retrieve(
            Branch._construct_id(model_id, branch_name)
        )

        if branch:

            commit = self.commit_storage.retrieve(branch.commit_id)

            return CommitResult(
                commit=commit,
                error=f"could not find commit with sha '{branch.commit_id}'" if commit is None else None,
            )

        else:
            return CommitResult(
                commit=None,
                error=f"could not find branch from branch name '{branch_name}' and model '{model_id}'",
            )