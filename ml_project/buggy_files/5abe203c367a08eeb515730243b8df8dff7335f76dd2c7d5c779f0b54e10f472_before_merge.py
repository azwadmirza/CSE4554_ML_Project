    def __init__(self, args):
        from dvc.repo import Repo
        from dvc.updater import Updater

        self.repo = Repo()
        self.config = self.repo.config
        self.args = args
        updater = Updater(self.repo.dvc_dir)
        updater.check()