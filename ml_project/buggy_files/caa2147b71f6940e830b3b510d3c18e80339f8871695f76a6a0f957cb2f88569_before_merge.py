    def set_config(self, cfg: DictConfig) -> None:
        assert cfg is not None
        OmegaConf.set_readonly(cfg.hydra, True)
        assert OmegaConf.get_type(cfg, "hydra") == HydraConf
        self.cfg = OmegaConf.masked_copy(cfg, "hydra")  # type: ignore