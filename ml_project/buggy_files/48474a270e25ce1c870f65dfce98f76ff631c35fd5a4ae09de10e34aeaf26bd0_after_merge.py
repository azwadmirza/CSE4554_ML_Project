    def __init__(self, repo_folder: Path):
        self._repo_folder = repo_folder

        self.author: Tuple[str, ...]
        self.install_msg: str
        self.short: str
        self.description: str

        self._info_file = repo_folder / self.INFO_FILE_NAME
        self._info: Dict[str, Any]

        self._read_info_file()