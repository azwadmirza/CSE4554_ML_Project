    async def hard_reset(self, branch: str = None) -> None:
        """Perform a hard reset on the current repo.

        Parameters
        ----------
        branch : `str`, optional
            Override for repo branch attribute.

        """
        if branch is None:
            branch = self.branch

        exists, _ = self._existing_git_repo()
        if not exists:
            raise MissingGitRepo("A git repo does not exist at path: {}".format(self.folder_path))

        p = await self._run(
            self.GIT_HARD_RESET.format(path=self.folder_path, branch=branch).split()
        )

        if p.returncode != 0:
            raise HardResetError(
                "Some error occurred when trying to"
                " execute a hard reset on the repo at"
                " the following path: {}".format(self.folder_path)
            )