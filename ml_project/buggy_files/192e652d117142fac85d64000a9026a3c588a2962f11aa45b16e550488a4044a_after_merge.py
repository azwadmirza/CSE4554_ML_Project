    async def update(self) -> (str, str):
        """Update the current branch of this repo.

        Returns
        -------
        `tuple` of `str`
            :py:code`(old commit hash, new commit hash)`

        """
        curr_branch = await self.current_branch()
        old_commit = await self.current_commit(branch=curr_branch)

        await self.hard_reset(branch=curr_branch)

        p = await self._run(self.GIT_PULL.format(path=self.folder_path).split())

        if p.returncode != 0:
            raise errors.UpdateError(
                "Git pull returned a non zero exit code"
                " for the repo located at path: {}".format(self.folder_path)
            )

        new_commit = await self.current_commit(branch=curr_branch)

        self._update_available_modules()
        self._read_info_file()

        return old_commit, new_commit