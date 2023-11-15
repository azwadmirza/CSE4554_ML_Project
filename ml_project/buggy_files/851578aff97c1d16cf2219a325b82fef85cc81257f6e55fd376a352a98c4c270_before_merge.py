    def run(self):
        import os
        from dvc.repo import Repo
        from dvc.updater import Updater

        root_dir = Repo.find_root()
        dvc_dir = os.path.join(root_dir, Repo.DVC_DIR)
        updater = Updater(dvc_dir)
        updater.fetch(detach=False)

        return 0