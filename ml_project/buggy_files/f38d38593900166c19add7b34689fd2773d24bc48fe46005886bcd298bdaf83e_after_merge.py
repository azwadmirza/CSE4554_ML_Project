    async def _get_file_update_statuses(
        self, old_rev: str, new_rev: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Gets the file update status letters for each changed file between the two revisions.

        Parameters
        ----------
        old_rev : `str`
            Pre-update revision
        new_rev : `str`, optional
            Post-update revision, defaults to repo's branch if not given

        Returns
        -------
        Dict[str, str]
            Mapping of filename -> status_letter

        """
        if new_rev is None:
            new_rev = self.branch
        git_command = ProcessFormatter().format(
            self.GIT_DIFF_FILE_STATUS, path=self.folder_path, old_rev=old_rev, new_rev=new_rev
        )
        p = await self._run(git_command)

        if p.returncode != 0:
            raise errors.GitDiffError(
                f"Git diff failed for repo at path: {self.folder_path}", git_command
            )

        stdout = p.stdout.strip(b"\t\n\x00 ").decode(**DECODE_PARAMS).split("\x00\t")
        ret = {}

        for filename in stdout:
            status, __, filepath = filename.partition("\x00")  # NUL character
            ret[filepath] = status

        return ret