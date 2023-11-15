    def __init__(self, dvc_dir, friendly=False, hardlink_lock=False):
        self.dvc_dir = dvc_dir
        self.updater_file = os.path.join(dvc_dir, self.UPDATER_FILE)
        self.lock = make_lock(
            self.updater_file + ".lock",
            tmp_dir=os.path.join(dvc_dir, "tmp"),
            friendly=friendly,
            hardlink_lock=hardlink_lock,
        )
        self.current = version.parse(__version__).base_version