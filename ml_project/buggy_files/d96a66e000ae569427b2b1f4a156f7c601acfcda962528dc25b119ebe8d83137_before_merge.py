    async def _get_commit_notes(self, old_rev: str, relative_file_path: str) -> str:
        """
        Gets the commit notes from git log.
        :param old_rev: Point in time to start getting messages
        :param relative_file_path: Path relative to the repo folder of the file
            to get messages for.
        :return: Git commit note log
        """
        git_command = ProcessFormatter().format(
            self.GIT_LOG,
            path=self.folder_path,
            old_rev=old_rev,
            relative_file_path=relative_file_path,
        )
        p = await self._run(git_command)

        if p.returncode != 0:
            raise errors.GitException(
                f"An exception occurred while executing git log on this repo: {self.folder_path}",
                git_command,
            )

        return p.stdout.decode().strip()