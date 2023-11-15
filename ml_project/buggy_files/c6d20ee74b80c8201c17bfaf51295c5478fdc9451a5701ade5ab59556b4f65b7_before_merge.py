    async def current_commit(self, branch: str = None) -> str:
        """Determine the current commit hash of the repo.

        Parameters
        ----------
        branch : `str`, optional
            Override for repo's branch attribute.

        Returns
        -------
        str
            The requested commit hash.

        """
        if branch is None:
            branch = self.branch

        exists, _ = self._existing_git_repo()
        if not exists:
            raise MissingGitRepo("A git repo does not exist at path: {}".format(self.folder_path))

        p = await self._run(
            self.GIT_LATEST_COMMIT.format(path=self.folder_path, branch=branch).split()
        )

        if p.returncode != 0:
            raise CurrentHashError("Unable to determine old commit hash.")

        return p.stdout.decode().strip()