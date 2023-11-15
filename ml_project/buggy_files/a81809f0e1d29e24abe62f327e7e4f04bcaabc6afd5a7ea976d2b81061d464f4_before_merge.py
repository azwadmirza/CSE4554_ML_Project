    async def current_commit(self) -> str:
        """Determine the current commit hash of the repo.

        Returns
        -------
        str
            The requested commit hash.

        """
        exists, __ = self._existing_git_repo()
        if not exists:
            raise errors.MissingGitRepo(f"A git repo does not exist at path: {self.folder_path}")

        git_command = ProcessFormatter().format(self.GIT_CURRENT_COMMIT, path=self.folder_path)
        p = await self._run(git_command)

        if p.returncode != 0:
            raise errors.CurrentHashError("Unable to determine commit hash.", git_command)

        return p.stdout.decode().strip()