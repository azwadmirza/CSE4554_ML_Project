    def __init__(self, repo):
        self.repo = repo
        self.root_dir = repo.root_dir
        self.tree = WorkingTree(self.root_dir)

        state_config = repo.config.get("state", {})
        self.row_limit = state_config.get("row_limit", self.STATE_ROW_LIMIT)
        self.row_cleanup_quota = state_config.get(
            "row_cleanup_quota", self.STATE_ROW_CLEANUP_QUOTA
        )

        if not repo.tmp_dir:
            self.state_file = None
            return

        self.state_file = os.path.join(repo.tmp_dir, self.STATE_FILE)

        # https://www.sqlite.org/tempfiles.html
        self.temp_files = [
            self.state_file + "-journal",
            self.state_file + "-wal",
        ]

        self.database = None
        self.cursor = None
        self.inserts = 0