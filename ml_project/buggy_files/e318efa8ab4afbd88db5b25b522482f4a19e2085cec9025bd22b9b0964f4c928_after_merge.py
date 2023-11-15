    def _init(self, **kwargs):
        global WANDB_ENABLED
        assert len(kwargs) == 0
        if WANDB_ENABLED:
            if self.monitoring_params is not None:
                self.checkpoints_glob: List[str] = \
                    self.monitoring_params.pop("checkpoints_glob", [])

                wandb.init(**self.monitoring_params)

                logdir_src = Path(self.logdir)
                logdir_dst = Path(wandb.run.dir)

                configs_src = logdir_src.joinpath("configs")
                os.makedirs(f"{logdir_dst}/{configs_src.name}", exist_ok=True)
                shutil.rmtree(f"{logdir_dst}/{configs_src.name}")
                shutil.copytree(
                    f"{str(configs_src.absolute())}",
                    f"{logdir_dst}/{configs_src.name}")

                code_src = logdir_src.joinpath("code")
                if code_src.exists():
                    os.makedirs(f"{logdir_dst}/{code_src.name}", exist_ok=True)
                    shutil.rmtree(f"{logdir_dst}/{code_src.name}")
                    shutil.copytree(
                        f"{str(code_src.absolute())}",
                        f"{logdir_dst}/{code_src.name}")
            else:
                WANDB_ENABLED = False
        self.wandb_mode = "trainer"