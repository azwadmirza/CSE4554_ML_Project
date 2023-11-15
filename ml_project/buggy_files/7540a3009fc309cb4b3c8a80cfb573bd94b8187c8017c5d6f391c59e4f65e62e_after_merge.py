    def __init__(self, root_dir=None):
        from dvc.config import Config
        from dvc.state import State
        from dvc.lock import Lock
        from dvc.scm import SCM
        from dvc.cache import Cache
        from dvc.data_cloud import DataCloud
        from dvc.updater import Updater
        from dvc.repo.metrics import Metrics
        from dvc.scm.tree import WorkingTree

        root_dir = self.find_root(root_dir)

        self.root_dir = os.path.abspath(os.path.realpath(root_dir))
        self.dvc_dir = os.path.join(self.root_dir, self.DVC_DIR)

        self.config = Config(self.dvc_dir)

        self.tree = WorkingTree()

        self.scm = SCM(self.root_dir, repo=self)
        self.lock = Lock(self.dvc_dir)
        # NOTE: storing state and link_state in the repository itself to avoid
        # any possible state corruption in 'shared cache dir' scenario.
        self.state = State(self, self.config.config)

        core = self.config.config[Config.SECTION_CORE]

        logger.set_level(core.get(Config.SECTION_CORE_LOGLEVEL))

        self.cache = Cache(self)
        self.cloud = DataCloud(self, config=self.config.config)
        self.updater = Updater(self.dvc_dir)

        self.metrics = Metrics(self)

        self._ignore()

        self.updater.check()