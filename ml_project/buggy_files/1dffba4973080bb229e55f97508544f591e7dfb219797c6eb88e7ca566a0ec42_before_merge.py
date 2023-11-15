    async def current_branch(self) -> str:
        """Determine the current branch using git commands.

        Returns
        -------
        str
            The current branch name.

        """
        exists, _ = self._existing_git_repo()
        if not exists:
            raise MissingGitRepo("A git repo does not exist at path: {}".format(self.folder_path))

        p = await self._run(self.GIT_CURRENT_BRANCH.format(path=self.folder_path).split())

        if p.returncode != 0:
            raise GitException(
                "Could not determine current branch at path: {}".format(self.folder_path)
            )

        return p.stdout.decode().strip()