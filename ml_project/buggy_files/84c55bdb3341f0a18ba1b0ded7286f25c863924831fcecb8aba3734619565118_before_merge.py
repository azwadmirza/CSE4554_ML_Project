    async def current_url(self, folder: Path = None) -> str:
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
        RuntimeError
            When the folder does not contain a git repo with a FETCH URL.
        """
        if folder is None:
            folder = self.folder_path

        p = await self._run(Repo.GIT_DISCOVER_REMOTE_URL.format(path=folder).split())

        if p.returncode != 0:
            raise RuntimeError("Unable to discover a repo URL.")

        return p.stdout.decode().strip()