    def __init__(self, args):
        from dvc.repo import Repo
        from dvc.updater import Updater

        self.repo = Repo()
        self.config = self.repo.config
        self.args = args
        hardlink_lock = self.config.config["core"].get("hardlink_lock", False)
        updater = Updater(self.repo.dvc_dir, hardlink_lock=hardlink_lock)
        updater.check()