    def set_config(self, cfg: DictConfig) -> None:
        assert cfg is not None
        OmegaConf.set_readonly(cfg.hydra, True)
        assert OmegaConf.get_type(cfg, "hydra") == HydraConf
        # THis is emulating a node that is hidden.
        # It's quiet a hack but it will be much better once
        # https://github.com/omry/omegaconf/issues/280 is done
        # The motivation is that this allows for interpolations from the hydra node
        # into the user's config.
        self.cfg = OmegaConf.masked_copy(cfg, "hydra")  # type: ignore
        self.cfg.hydra._set_parent(cfg)  # type: ignore