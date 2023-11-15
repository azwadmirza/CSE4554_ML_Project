    async def current_url(self, folder: Optional[Path] = None) -> str:
        """
        Discovers the FETCH URL for a Git repo.

        Parameters
        ----------
        folder : pathlib.Path
            The folder to search for a URL.

        Returns
        -------
        str
            The FETCH URL.

        Raises
        ------
        .NoRemoteURL
            When the folder does not contain a git repo with a FETCH URL.

        """
        if folder is None:
            folder = self.folder_path

        git_command = ProcessFormatter().format(Repo.GIT_DISCOVER_REMOTE_URL, path=folder)
        p = await self._run(git_command)

        if p.returncode != 0:
            raise errors.NoRemoteURL("Unable to discover a repo URL.", git_command)

        return p.stdout.decode(**DECODE_PARAMS).strip()