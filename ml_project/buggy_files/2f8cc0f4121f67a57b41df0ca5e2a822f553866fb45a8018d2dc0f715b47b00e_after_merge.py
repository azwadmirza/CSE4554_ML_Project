    async def clone(self) -> Tuple[str]:
        """Clone a new repo.

        Returns
        -------
        `tuple` of `str`
            All available module names from this repo.

        """
        exists, path = self._existing_git_repo()
        if exists:
            raise errors.ExistingGitRepo("A git repo already exists at path: {}".format(path))

        if self.branch is not None:
            p = await self._run(
                self.GIT_CLONE.format(
                    branch=self.branch, url=self.url, folder=self.folder_path
                ).split()
            )
        else:
            p = await self._run(
                self.GIT_CLONE_NO_BRANCH.format(url=self.url, folder=self.folder_path).split()
            )

        if p.returncode:
            # Try cleaning up folder
            shutil.rmtree(str(self.folder_path), ignore_errors=True)
            raise errors.CloningError("Error when running git clone.")

        if self.branch is None:
            self.branch = await self.current_branch()

        self._read_info_file()

        return self._update_available_modules()