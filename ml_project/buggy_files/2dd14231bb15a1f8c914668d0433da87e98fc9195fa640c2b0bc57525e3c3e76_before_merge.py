    def __init__(self, location: Path, repo: Optional[Repo] = None, commit: str = ""):
        """Base installable initializer.

        Parameters
        ----------
        location : pathlib.Path
            Location (file or folder) to the installable.
        repo : Repo, optional
            Repo object of the Installable, if repo is missing this will be `None`
        commit : str
            Installable's commit. This is not the same as ``repo.commit``

        """
        super().__init__(location)

        self._location = location

        self.repo = repo
        self.repo_name = self._location.parent.stem
        self.commit = commit

        self.min_bot_version = red_version_info
        self.max_bot_version = red_version_info
        self.min_python_version = (3, 5, 1)
        self.hidden = False
        self.disabled = False
        self.required_cogs: Dict[str, str] = {}  # Cog name -> repo URL
        self.requirements: Tuple[str, ...] = ()
        self.tags: Tuple[str, ...] = ()
        self.type = InstallableType.UNKNOWN

        if self._info_file.exists():
            self._process_info_file(self._info_file)

        if self._info == {}:
            self.type = InstallableType.COG