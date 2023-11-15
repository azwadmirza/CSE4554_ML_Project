    def __init__(self, repo_folder: Path):
        self._repo_folder = repo_folder

        self.author: Tuple[str, ...] = ()
        self.install_msg: Optional[str] = None
        self.short: Optional[str] = None
        self.description: Optional[str] = None

        self._info_file = repo_folder / self.INFO_FILE_NAME
        if self._info_file.exists():
            self._read_info_file()

        self._info: Dict[str, Any] = {}