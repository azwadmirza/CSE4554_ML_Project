    def __init__(
        self,
        env_setup: DictConfig,
        ray: RayAWSConf,
        stop_cluster: bool,
        sync_up: RsyncConf,
        sync_down: RsyncConf,
    ) -> None:
        self.ray_cfg = ray
        self.stop_cluster = stop_cluster
        self.sync_up = sync_up
        self.sync_down = sync_down
        self.config: Optional[DictConfig] = None
        self.config_loader: Optional[ConfigLoader] = None
        self.task_function: Optional[TaskFunction] = None
        self.ray_yaml_path: Optional[str] = None
        self.env_setup = env_setup