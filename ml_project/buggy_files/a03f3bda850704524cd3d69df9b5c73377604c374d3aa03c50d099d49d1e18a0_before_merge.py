    async def _get_commit_notes(self, old_commit_hash: str, relative_file_path: str) -> str:
        """
        Gets the commit notes from git log.
        :param old_commit_hash: Point in time to start getting messages
        :param relative_file_path: Path relative to the repo folder of the file
            to get messages for.
        :return: Git commit note log
        """
        p = await self._run(
            self.GIT_LOG.format(
                path=self.folder_path,
                old_hash=old_commit_hash,
                relative_file_path=relative_file_path,
            )
        )

        if p.returncode != 0:
            raise GitException(
                "An exception occurred while executing git log on"
                " this repo: {}".format(self.folder_path)
            )

        return p.stdout.decode().strip()