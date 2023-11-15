    def __init__(self, dvc_dir):
        self.dvc_dir = dvc_dir
        self.updater_file = os.path.join(dvc_dir, self.UPDATER_FILE)
        self.lock = Lock(
            self.updater_file + ".lock", tmp_dir=os.path.join(dvc_dir, "tmp")
        )
        self.current = version.parse(__version__).base_version