    def set_config(self, cfg: DictConfig) -> None:
        assert cfg is not None
        self.hydra = copy.deepcopy(cfg.hydra)
        OmegaConf.set_readonly(self.hydra, True)  # type: ignore