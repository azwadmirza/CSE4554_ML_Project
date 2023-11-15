    async def _get_file_update_statuses(
        self, old_hash: str, new_hash: str
    ) -> MutableMapping[str, str]:
        """
        Gets the file update status letters for each changed file between
            the two hashes.
        :param old_hash: Pre-update
        :param new_hash: Post-update
        :return: Mapping of filename -> status_letter
        """
        p = await self._run(
            self.GIT_DIFF_FILE_STATUS.format(
                path=self.folder_path, old_hash=old_hash, new_hash=new_hash
            )
        )

        if p.returncode != 0:
            raise GitDiffError("Git diff failed for repo at path: {}".format(self.folder_path))

        stdout = p.stdout.strip().decode().split("\n")

        ret = {}

        for filename in stdout:
            # TODO: filter these filenames by ones in self.available_modules
            status, _, filepath = filename.partition("\t")
            ret[filepath] = status

        return ret