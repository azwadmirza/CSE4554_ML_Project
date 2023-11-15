    def run(self):
        import os
        from dvc.repo import Repo
        from dvc.config import Config
        from dvc.updater import Updater

        root_dir = Repo.find_root()
        dvc_dir = os.path.join(root_dir, Repo.DVC_DIR)
        config = Config(dvc_dir, verify=False)
        hardlink_lock = config.config.get("core", {}).get(
            "hardlink_lock", False
        )
        updater = Updater(dvc_dir, hardlink_lock=hardlink_lock)
        updater.fetch(detach=False)

        return 0