    async def current_branch(self) -> str:
        """Determine the current branch using git commands.

        Returns
        -------
        str
            The current branch name.

        """
        exists, __ = self._existing_git_repo()
        if not exists:
            raise errors.MissingGitRepo(f"A git repo does not exist at path: {self.folder_path}")

        git_command = ProcessFormatter().format(self.GIT_CURRENT_BRANCH, path=self.folder_path)
        p = await self._run(git_command)

        if p.returncode != 0:
            raise errors.GitException(
                f"Could not determine current branch at path: {self.folder_path}", git_command
            )

        return p.stdout.decode().strip()