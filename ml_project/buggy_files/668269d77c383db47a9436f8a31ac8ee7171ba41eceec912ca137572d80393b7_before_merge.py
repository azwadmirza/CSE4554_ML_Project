    def _init(self, **kwargs):
        global WANDB_ENABLED
        assert len(kwargs) == 0
        if WANDB_ENABLED:
            if self.monitoring_params is not None:
                self.checkpoints_glob: List[str] = \
                    self.monitoring_params.pop(
                        "checkpoints_glob", ["best.pth", "last.pth"])

                wandb.init(**self.monitoring_params)
            else:
                WANDB_ENABLED = False
        self.wandb_mode = "sampler"