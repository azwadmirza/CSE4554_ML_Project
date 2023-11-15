    def run(self):
        CleanCommand.run(self)
        delete_in_root = ["build", ".cache", "dist", ".eggs", "*.egg-info", ".tox"]
        delete_everywhere = ["__pycache__", "*.pyc"]
        for candidate in delete_in_root:
            rmtree_glob(candidate)
        for visible_dir in glob("[A-Za-z0-9]*"):
            for candidate in delete_everywhere:
                rmtree_glob(join(visible_dir, candidate))
                rmtree_glob(join(visible_dir, "*", candidate))