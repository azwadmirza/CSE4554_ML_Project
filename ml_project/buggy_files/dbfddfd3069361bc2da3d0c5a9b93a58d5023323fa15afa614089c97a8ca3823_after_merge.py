    def __init__(  # pylint:disable=W0231
        self, root_dir=os.curdir, search_parent_directories=True
    ):
        from dulwich.errors import NotGitRepository
        from dulwich.repo import Repo

        try:
            if search_parent_directories:
                self.repo = Repo.discover(start=root_dir)
            else:
                self.repo = Repo(root_dir)
        except NotGitRepository as exc:
            raise SCMError(f"{root_dir} is not a git repository") from exc

        self._submodules: Dict[str, "PathInfo"] = self._find_submodules()
        self._stashes: dict = {}